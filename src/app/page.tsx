import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Activity, ShieldCheck, Zap, Database } from 'lucide-react';

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-background">
      <header className="px-6 py-4 flex items-center justify-between border-b bg-card shadow-sm">
        <div className="flex items-center gap-2">
          <Activity className="text-primary h-8 w-8" />
          <span className="text-2xl font-bold font-headline tracking-tight text-primary">DiseaseAI</span>
        </div>
        <nav className="flex gap-4">
          <Link href="/login">
            <Button variant="ghost">Login</Button>
          </Link>
          <Link href="/signup">
            <Button>Get Started</Button>
          </Link>
        </nav>
      </header>

      <main className="flex-1">
        <section className="py-20 px-6 max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-7xl font-bold font-headline mb-6 tracking-tight text-foreground">
            Precision AI for <span className="text-primary">Early Detection</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
            A state-of-the-art diagnostic system combining custom PyTorch CNN models with cloud scalability to deliver instant medical image analysis.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/signup">
              <Button size="lg" className="h-14 px-10 text-lg rounded-full">
                Start Diagnosis
              </Button>
            </Link>
            <Link href="#features">
              <Button size="lg" variant="outline" className="h-14 px-10 text-lg rounded-full">
                Learn More
              </Button>
            </Link>
          </div>
        </section>

        <section id="features" className="py-20 bg-secondary/30">
          <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-3 gap-8">
            <Card className="border-none shadow-md">
              <CardContent className="pt-8">
                <Zap className="h-12 w-12 text-accent mb-4" />
                <h3 className="text-xl font-bold mb-2">Instant Analysis</h3>
                <p className="text-muted-foreground">
                  Our custom-trained CNN models process medical images in milliseconds, providing real-time diagnostic indicators.
                </p>
              </CardContent>
            </Card>
            <Card className="border-none shadow-md">
              <CardContent className="pt-8">
                <ShieldCheck className="h-12 w-12 text-primary mb-4" />
                <h3 className="text-xl font-bold mb-2">Secure Storage</h3>
                <p className="text-muted-foreground">
                  All medical records and images are protected with enterprise-grade encryption and Firebase security rules.
                </p>
              </CardContent>
            </Card>
            <Card className="border-none shadow-md">
              <CardContent className="pt-8">
                <Database className="h-12 w-12 text-blue-500 mb-4" />
                <h3 className="text-xl font-bold mb-2">Detailed History</h3>
                <p className="text-muted-foreground">
                  Keep track of all your diagnostic sessions with a clean, intuitive dashboard that persists across all devices.
                </p>
              </CardContent>
            </Card>
          </div>
        </section>
      </main>

      <footer className="py-8 px-6 border-t bg-card text-center text-sm text-muted-foreground">
        © 2024 DiseaseAI System. For clinical research purposes only.
      </footer>
    </div>
  );
}
