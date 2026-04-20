import { NextRequest, NextResponse } from 'next/server';

const AI_BACKEND_URL = process.env.AI_BACKEND_URL || 'http://localhost:8080';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;
    const description = formData.get('description') as string;

    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 });
    }

    // Forward the file and clinical description to the Python AI backend
    const backendFormData = new FormData();
    backendFormData.append('file', file);
    if (description) {
      backendFormData.append('description', description);
    }

    const response = await fetch(`${AI_BACKEND_URL}/predict`, {
      method: 'POST',
      body: backendFormData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'AI backend error' }));
      return NextResponse.json(
        { error: errorData.detail || 'Prediction failed' },
        { status: response.status }
      );
    }

    const result = await response.json();
    return NextResponse.json(result);
  } catch (error: any) {
    console.error('[API /predict] Error:', error.message);
    return NextResponse.json(
      { error: 'AI backend is not available. Make sure the Python server is running on port 8080.' },
      { status: 503 }
    );
  }
}
