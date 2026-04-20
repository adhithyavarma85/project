"use client"

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { Activity, LayoutDashboard, History, Settings, LogOut, Search, Loader2, Send, Upload, FileText, Clock, AlertTriangle, CheckCircle2, XCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { UploadZone } from '@/components/diagnosis/UploadZone'
import { Separator } from '@/components/ui/separator'
import { useUser, useFirestore, useCollection, useMemoFirebase } from '@/firebase'
import { collection, query, orderBy, doc, setDoc, serverTimestamp } from 'firebase/firestore'
import { signOut } from 'firebase/auth'
import { useAuth } from '@/firebase'
import { cn } from '@/lib/utils'

export default function Dashboard() {
  const { user, isUserLoading } = useUser()
  const auth = useAuth()
  const db = useFirestore()
  const router = useRouter()
  
  const [isUploading, setIsUploading] = useState(false)
  const [predictionStatus, setPredictionStatus] = useState<'idle' | 'uploading' | 'analyzing' | 'complete'>('idle')
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant', content: string }[]>([
    { role: 'assistant', content: "Welcome. Please describe the patient symptoms before uploading the medical scan for analysis." }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const [activeTab, setActiveTab] = useState('new')

  const historyQuery = useMemoFirebase(() => {
    if (!db || !user) return null
    return query(
      collection(db, 'user_profiles', user.uid, 'diagnostic_results'),
      orderBy('uploadTimestamp', 'desc')
    )
  }, [db, user])

  const { data: history, isLoading: isHistoryLoading } = useCollection(historyQuery)

  useEffect(() => {
    if (!isUserLoading && !user) {
      router.push('/login')
    }
  }, [user, isUserLoading, router])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleSignOut = async () => {
    await signOut(auth)
    router.push('/login')
  }

  const handleSendMessage = (e?: React.FormEvent) => {
    e?.preventDefault()
    if (!inputValue.trim()) return

    setMessages(prev => [...prev, { role: 'user', content: inputValue }])
    const currentInput = inputValue
    setInputValue('')
    
    setIsTyping(true)
    setTimeout(() => {
      setIsTyping(false)
      const lower = currentInput.toLowerCase()
      if (lower.includes('pain') || lower.includes('fever') || lower.includes('headache') || lower.includes('seizure') || lower.includes('cough')) {
        setMessages(prev => [...prev, { role: 'assistant', content: "Symptoms recorded. Please upload the medical scan now. The system will correlate your clinical history with the image analysis." }])
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: "Noted. Any additional symptoms to report before uploading the scan?" }])
      }
    }, 1200)
  }

  const handleUpload = async (file: File) => {
    if (!user) return

    setIsUploading(true)
    setPredictionStatus('uploading')
    
    try {
      const description = messages
        .filter(m => m.role === 'user')
        .map(m => m.content)
        .join(". ")

      const formData = new FormData()
      formData.append('file', file)
      if (description.trim()) {
        formData.append('description', description)
      }

      setPredictionStatus('analyzing')

      const response = await fetch('/api/predict', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }))
        throw new Error(errorData.error || 'Prediction failed')
      }

      const aiResult = await response.json()

      const resultId = Math.random().toString(36).substr(2, 9)
      const newResult = {
        id: resultId,
        userId: user.uid,
        imageStoragePath: URL.createObjectURL(file),
        originalFileName: file.name,
        uploadTimestamp: new Date().toISOString(),
        diagnosisTimestamp: new Date().toISOString(),
        diseasePrediction: aiResult.prediction || 'Unknown',
        imageConfidence: aiResult.image_confidence ?? 0,
        symptomConfidence: aiResult.symptom_confidence ?? 0,
        finalConfidence: aiResult.final_confidence ?? 0,
        verdict: aiResult.verdict || '',
        status: aiResult.status || 'Normal',
        extractedMedicalTerms: aiResult.extracted_medical_terms || [],
        clinicalReasoning: aiResult.clinical_reasoning || '',
        severity: aiResult.severity || 'Unknown',
        description: aiResult.description || '',
        recommendation: aiResult.recommendation || '',
        inferenceTimeMs: aiResult.inference_time_ms || 0,
        top3Predictions: aiResult.top3_predictions || [],
        userNotes: description,
        bestNlpMatch: aiResult.best_nlp_match || '',
        hasDissonance: aiResult.has_dissonance || false
      }

      const resultDocRef = doc(db, 'user_profiles', user.uid, 'diagnostic_results', resultId)
      setDoc(resultDocRef, newResult)

      setPredictionStatus('complete')
      setMessages([{ role: 'assistant', content: "Analysis complete. Results are available in the Records tab." }])
      setActiveTab('history')
    } catch (error: any) {
      console.error('Diagnosis error:', error)
      setPredictionStatus('idle')
      alert(`Diagnosis failed: ${error.message}. Make sure the Python AI backend is running.`)
    } finally {
      setIsUploading(false)
      setTimeout(() => setPredictionStatus('idle'), 3000)
    }
  }

  if (isUserLoading) {
    return (
      <div className="h-screen w-screen flex flex-col items-center justify-center gap-4 bg-slate-50">
        <Loader2 className="h-8 w-8 animate-spin text-slate-600" />
        <p className="text-sm text-slate-500">Loading clinical portal</p>
      </div>
    )
  }

  if (!user) return null

  const statusColor = (s: string) => s === 'Critical' ? 'text-red-600 bg-red-50 border-red-200' : s === 'Alert' ? 'text-amber-600 bg-amber-50 border-amber-200' : 'text-emerald-600 bg-emerald-50 border-emerald-200'

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden" style={{ fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif" }}>

      {/* Sidebar */}
      <aside className="w-56 bg-white border-r border-slate-200 flex flex-col">
        <div className="px-5 py-5 flex items-center gap-2.5 border-b border-slate-100">
          <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center">
            <Activity className="text-white h-4 w-4" />
          </div>
          <span className="text-sm tracking-tight text-slate-800" style={{ fontWeight: 600 }}>DiseaseAI</span>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          <Button 
            variant={activeTab === 'new' ? 'secondary' : 'ghost'} 
            className="w-full justify-start gap-3 h-10 rounded-lg text-xs"
            onClick={() => setActiveTab('new')}
            style={{ fontWeight: 500 }}
          >
            <LayoutDashboard className="h-4 w-4" />
            Diagnosis Center
          </Button>
          <Button 
            variant={activeTab === 'history' ? 'secondary' : 'ghost'} 
            className="w-full justify-start gap-3 h-10 rounded-lg text-xs"
            onClick={() => setActiveTab('history')}
            style={{ fontWeight: 500 }}
          >
            <History className="h-4 w-4" />
            Patient Records
          </Button>
          <Button variant="ghost" className="w-full justify-start gap-3 h-10 rounded-lg text-xs" style={{ fontWeight: 500 }}>
            <Settings className="h-4 w-4" />
            Settings
          </Button>
        </nav>
        <div className="px-3 py-4 border-t border-slate-100">
          <Button 
            variant="ghost" 
            className="w-full justify-start gap-3 h-10 rounded-lg text-xs text-red-500 hover:bg-red-50 hover:text-red-600"
            onClick={handleSignOut}
            style={{ fontWeight: 500 }}
          >
            <LogOut className="h-4 w-4" />
            Sign Out
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        {/* Top Bar */}
        <div className="bg-white border-b border-slate-200 px-8 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-lg text-slate-800" style={{ fontWeight: 600 }}>Clinical Diagnosis System</h1>
            <div className="flex items-center gap-3 mt-1">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
              <p className="text-xs text-slate-400">Bio-ClinicalBERT Engine Active</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400" />
              <Input placeholder="Search records" className="pl-8 w-48 h-8 rounded-md text-xs border-slate-200 bg-slate-50" />
            </div>
            <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs" style={{ fontWeight: 500 }}>
              {user?.displayName?.charAt(0) || user?.email?.charAt(0) || 'U'}
            </div>
          </div>
        </div>

        <div className="p-8">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="bg-white border border-slate-200 p-0.5 rounded-lg mb-8 h-9">
              <TabsTrigger value="new" className="rounded-md px-6 text-xs data-[state=active]:bg-blue-600 data-[state=active]:text-white" style={{ fontWeight: 500 }}>New Scan</TabsTrigger>
              <TabsTrigger value="history" className="rounded-md px-6 text-xs data-[state=active]:bg-blue-600 data-[state=active]:text-white" style={{ fontWeight: 500 }}>Records</TabsTrigger>
            </TabsList>

            {/* ====== NEW SCAN TAB ====== */}
            <TabsContent value="new">
              <div className="grid lg:grid-cols-5 gap-6">

                {/* Upload Section */}
                <div className="lg:col-span-3 space-y-6">
                  <div className="bg-white rounded-xl border border-slate-200 p-6">
                    <div className="flex items-center gap-2 mb-4">
                      <Upload className="h-4 w-4 text-slate-500" />
                      <h2 className="text-sm text-slate-700" style={{ fontWeight: 600 }}>Upload Medical Image</h2>
                    </div>
                    <UploadZone 
                      onUpload={handleUpload} 
                      isUploading={isUploading} 
                      predictionStatus={predictionStatus} 
                    />
                    <p className="text-xs text-slate-400 mt-3">Supported: JPEG, PNG, BMP, TIFF, WebP. Max 10MB.</p>
                  </div>

                  {/* System Status */}
                  <div className="bg-white rounded-xl border border-slate-200 p-5">
                    <div className="flex items-center gap-2 mb-4">
                      <FileText className="h-4 w-4 text-slate-500" />
                      <h2 className="text-sm text-slate-700" style={{ fontWeight: 600 }}>System Modules</h2>
                    </div>
                    <div className="grid grid-cols-3 gap-3">
                      <div className="rounded-lg bg-slate-50 border border-slate-100 p-3">
                        <p className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">Vision</p>
                        <p className="text-xs text-slate-700" style={{ fontWeight: 500 }}>ResNet-50 v2</p>
                        <span className="inline-block mt-1.5 text-[9px] px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-600 border border-emerald-100">Active</span>
                      </div>
                      <div className="rounded-lg bg-slate-50 border border-slate-100 p-3">
                        <p className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">NLP</p>
                        <p className="text-xs text-slate-700" style={{ fontWeight: 500 }}>ClinicalBERT</p>
                        <span className="inline-block mt-1.5 text-[9px] px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-600 border border-emerald-100">Active</span>
                      </div>
                      <div className="rounded-lg bg-slate-50 border border-slate-100 p-3">
                        <p className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">NER</p>
                        <p className="text-xs text-slate-700" style={{ fontWeight: 500 }}>Medical NER</p>
                        <span className="inline-block mt-1.5 text-[9px] px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-600 border border-emerald-100">Active</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Chat Section */}
                <div className="lg:col-span-2">
                  <div className="bg-white rounded-xl border border-slate-200 flex flex-col h-[540px]">
                    <div className="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between">
                      <div className="flex items-center gap-2.5">
                        <div className="h-8 w-8 rounded-lg bg-blue-50 flex items-center justify-center">
                          <Activity className="h-4 w-4 text-blue-600" />
                        </div>
                        <div>
                          <p className="text-sm text-slate-700" style={{ fontWeight: 600 }}>AI Doctor</p>
                          <div className="flex items-center gap-1.5">
                            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                            <p className="text-[10px] text-slate-400">Online</p>
                          </div>
                        </div>
                      </div>
                      <span className="text-[9px] text-slate-400 px-2 py-0.5 rounded bg-slate-50 border border-slate-100">v2.5</span>
                    </div>

                    {/* Messages */}
                    <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50">
                      {messages.map((m, idx) => (
                        <div key={idx} className={cn("flex gap-2.5", m.role === 'user' ? "flex-row-reverse" : "flex-row")}>
                          <div className={cn(
                            "h-7 w-7 rounded-full flex-shrink-0 flex items-center justify-center text-xs",
                            m.role === 'user' ? "bg-blue-600 text-white" : "bg-white border border-slate-200 text-blue-600"
                          )}>
                            {m.role === 'user' ? 'P' : <Activity className="h-3 w-3" />}
                          </div>
                          <div className={cn(
                            "max-w-[85%] px-3.5 py-2.5 rounded-xl text-xs leading-relaxed",
                            m.role === 'user' 
                              ? "bg-blue-600 text-white rounded-tr-sm" 
                              : "bg-white border border-slate-200 text-slate-600 rounded-tl-sm"
                          )} style={{ fontWeight: 400 }}>
                            {m.content}
                          </div>
                        </div>
                      ))}
                      {isTyping && (
                        <div className="flex gap-2.5">
                          <div className="h-7 w-7 rounded-full bg-white border border-slate-200 flex items-center justify-center text-blue-600">
                            <Activity className="h-3 w-3" />
                          </div>
                          <div className="bg-white border border-slate-200 rounded-xl rounded-tl-sm px-4 py-2.5 flex gap-1 items-center">
                            <span className="h-1 w-1 rounded-full bg-slate-300 animate-bounce" style={{ animationDelay: '0ms' }} />
                            <span className="h-1 w-1 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                            <span className="h-1 w-1 rounded-full bg-slate-500 animate-bounce" style={{ animationDelay: '300ms' }} />
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Input */}
                    <form onSubmit={handleSendMessage} className="p-3 border-t border-slate-100 flex gap-2">
                      <Input 
                        placeholder="Describe symptoms..." 
                        className="flex-1 h-9 rounded-lg text-xs border-slate-200 bg-white"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        style={{ fontWeight: 400 }}
                      />
                      <Button 
                        type="submit"
                        size="icon"
                        className="h-9 w-9 rounded-lg bg-blue-600 hover:bg-blue-700"
                        disabled={!inputValue.trim()}
                      >
                        <Send className="h-3.5 w-3.5" />
                      </Button>
                    </form>
                  </div>
                </div>
              </div>
            </TabsContent>

            {/* ====== RECORDS TAB ====== */}
            <TabsContent value="history">
              <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
                {/* Table Header */}
                <div className="grid grid-cols-12 gap-4 px-6 py-3 bg-slate-50 border-b border-slate-200 text-[10px] text-slate-400 uppercase tracking-wider">
                  <div className="col-span-1">Scan</div>
                  <div className="col-span-3">Diagnosis</div>
                  <div className="col-span-3">Clinical Reasoning</div>
                  <div className="col-span-1 text-center">Image</div>
                  <div className="col-span-1 text-center">NLP</div>
                  <div className="col-span-1 text-center">Fused</div>
                  <div className="col-span-2 text-center">Status</div>
                </div>

                {isHistoryLoading ? (
                  <div className="py-20 text-center">
                    <Loader2 className="h-6 w-6 animate-spin text-slate-400 mx-auto mb-3" />
                    <p className="text-xs text-slate-400">Loading records</p>
                  </div>
                ) : history && history.length > 0 ? (
                  <div className="divide-y divide-slate-100">
                    {history.map((item) => (
                      <div key={item.id} className="grid grid-cols-12 gap-4 px-6 py-4 items-center hover:bg-slate-50/50 transition-colors">
                        {/* Thumbnail */}
                        <div className="col-span-1">
                          <div className="h-12 w-12 rounded-lg overflow-hidden border border-slate-200 bg-slate-100">
                            {/* eslint-disable-next-line @next/next/no-img-element */}
                            <img src={item.imageStoragePath} alt="Scan" className="w-full h-full object-cover" />
                          </div>
                        </div>

                        {/* Diagnosis */}
                        <div className="col-span-3">
                          <div className="flex items-center gap-2 mb-1">
                            <p className="text-sm text-slate-800" style={{ fontWeight: 600 }}>{item.diseasePrediction}</p>
                            {item.hasDissonance && (
                              <span className="text-[9px] px-1.5 py-0.5 rounded bg-amber-50 text-amber-600 border border-amber-200 flex items-center gap-1">
                                <AlertTriangle className="h-2.5 w-2.5" />
                                Dissonance
                              </span>
                            )}
                          </div>
                          {item.hasDissonance && item.bestNlpMatch && (
                            <p className="text-[10px] text-blue-600">NLP suggests: {item.bestNlpMatch}</p>
                          )}
                          {item.extractedMedicalTerms && item.extractedMedicalTerms.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-1.5">
                              {item.extractedMedicalTerms.slice(0, 4).map((term: string) => (
                                <span key={term} className="text-[9px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-500 border border-slate-200">{term}</span>
                              ))}
                            </div>
                          )}
                        </div>

                        {/* Reasoning */}
                        <div className="col-span-3">
                          <p className="text-[11px] text-slate-500 leading-relaxed line-clamp-3" style={{ fontWeight: 400 }}>
                            {item.clinicalReasoning || "Standard analysis complete."}
                          </p>
                        </div>

                        {/* Image Score */}
                        <div className="col-span-1 text-center">
                          <p className="text-sm text-slate-700 tabular-nums" style={{ fontWeight: 500 }}>{(item.imageConfidence ?? 0).toFixed(1)}%</p>
                          <div className="h-1 w-full bg-slate-100 rounded-full mt-1 overflow-hidden">
                            <div className="h-full bg-blue-500 rounded-full" style={{ width: `${item.imageConfidence ?? 0}%` }} />
                          </div>
                        </div>

                        {/* NLP Score */}
                        <div className="col-span-1 text-center">
                          <p className="text-sm text-slate-700 tabular-nums" style={{ fontWeight: 500 }}>{(item.symptomConfidence ?? 0).toFixed(1)}%</p>
                          <div className="h-1 w-full bg-slate-100 rounded-full mt-1 overflow-hidden">
                            <div className="h-full bg-violet-500 rounded-full" style={{ width: `${item.symptomConfidence ?? 0}%` }} />
                          </div>
                        </div>

                        {/* Fused Score */}
                        <div className="col-span-1 text-center">
                          <p className="text-lg text-blue-600 tabular-nums" style={{ fontWeight: 600 }}>{(item.finalConfidence ?? 0).toFixed(1)}%</p>
                        </div>

                        {/* Status */}
                        <div className="col-span-2 flex justify-center">
                          <span className={cn(
                            "text-[10px] px-3 py-1 rounded-full border flex items-center gap-1.5",
                            statusColor(item.status || 'Normal')
                          )} style={{ fontWeight: 500 }}>
                            {item.status === 'Critical' && <XCircle className="h-3 w-3" />}
                            {item.status === 'Alert' && <AlertTriangle className="h-3 w-3" />}
                            {(item.status === 'Normal' || !item.status) && <CheckCircle2 className="h-3 w-3" />}
                            {item.status || "Healthy"}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="py-20 text-center">
                    <div className="h-12 w-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto mb-3">
                      <FileText className="h-5 w-5 text-slate-300" />
                    </div>
                    <p className="text-sm text-slate-500 mb-1" style={{ fontWeight: 500 }}>No records found</p>
                    <p className="text-xs text-slate-400 mb-4">Start a new diagnosis to build patient history.</p>
                    <Button 
                      variant="outline" 
                      className="rounded-lg text-xs h-8 px-4"
                      onClick={() => setActiveTab('new')}
                      style={{ fontWeight: 500 }}
                    >
                      New Scan
                    </Button>
                  </div>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  )
}
