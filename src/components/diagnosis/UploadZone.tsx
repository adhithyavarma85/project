"use client"

import { useState, useCallback } from 'react'
import { Upload, X, Loader2, CheckCircle2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Card } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface UploadZoneProps {
  onUpload: (file: File) => Promise<void>
  isUploading: boolean
  predictionStatus: 'idle' | 'uploading' | 'analyzing' | 'complete'
}

export function UploadZone({ onUpload, isUploading, predictionStatus }: UploadZoneProps) {
  const [dragActive, setDragActive] = useState(false)
  const [file, setFile] = useState<File | null>(null)

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0])
    }
  }, [])

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }, [])

  const startAnalysis = () => {
    if (file) {
      onUpload(file)
    }
  }

  const clear = () => setFile(null)

  return (
    <Card className="p-8 border-dashed border-2 bg-card/50">
      {!file ? (
        <div
          className={cn(
            "flex flex-col items-center justify-center py-12 transition-colors",
            dragActive ? "bg-primary/5" : "bg-transparent"
          )}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <Upload className="h-12 w-12 text-muted-foreground mb-4" />
          <p className="text-lg font-medium mb-1">Drag and drop medical image</p>
          <p className="text-sm text-muted-foreground mb-6">Supports DICOM, JPG, PNG (Max 10MB)</p>
          <input
            type="file"
            className="hidden"
            id="file-upload"
            accept="image/*"
            onChange={handleChange}
          />
          <label htmlFor="file-upload">
            <Button variant="outline" asChild>
              <span className="cursor-pointer">Browse Files</span>
            </Button>
          </label>
        </div>
      ) : (
        <div className="flex flex-col items-center py-4">
          <div className="relative w-full max-w-xs aspect-square rounded-lg overflow-hidden border mb-6">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img 
              src={URL.createObjectURL(file)} 
              alt="Preview" 
              className="w-full h-full object-cover"
            />
            {!isUploading && (
              <Button
                variant="destructive"
                size="icon"
                className="absolute top-2 right-2 rounded-full"
                onClick={clear}
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
          
          <div className="w-full max-w-md space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium truncate max-w-[200px]">{file.name}</span>
              <span className="text-xs text-muted-foreground">{(file.size / (1024 * 1024)).toFixed(2)} MB</span>
            </div>
            
            {predictionStatus === 'uploading' && (
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span>Uploading to Secure Storage...</span>
                </div>
                <Progress value={45} className="h-1" />
              </div>
            )}

            {predictionStatus === 'analyzing' && (
              <div className="flex items-center justify-center gap-2 text-primary font-medium">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>AI Engine Analysis in progress...</span>
              </div>
            )}

            {predictionStatus === 'complete' && (
              <div className="flex items-center justify-center gap-2 text-green-600 font-medium">
                <CheckCircle2 className="h-4 w-4" />
                <span>Analysis Complete</span>
              </div>
            )}

            {predictionStatus === 'idle' && (
              <Button className="w-full h-12" onClick={startAnalysis}>
                Run AI Diagnosis
              </Button>
            )}
          </div>
        </div>
      )}
    </Card>
  )
}
