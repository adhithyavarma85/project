# Welcome to Antigravity!

Welcome to your new developer home! Your Firebase Studio project has been successfully migrated to Antigravity.

Antigravity is our next-generation, agent-first IDE designed for high-velocity, autonomous development. Because Antigravity runs locally on your machine, you now have access to powerful local workflows and fully integrated AI editing capabilities that go beyond a cloud-based web IDE.

## Getting Started
- **Run Locally**: Use the **Run and Debug** menu on the left sidebar to start your local development server.
  - Or in a terminal run `npm run dev` and visit `http://localhost:9002`.
- **Deploy**: You can deploy your changes to Firebase App Hosting by using the integrated terminal and standard Firebase CLI commands, just as you did in Firebase Studio.
- **Cleanup**: Cleanup unused artifacts with the @cleanup workflow.

Enjoy the next era of AI-driven development!

File any bugs at https://github.com/firebase/firebase-tools/issues

**Firebase Studio Export Date:** 2026-03-20


---

## Previous README.md contents:

# Disease AI System - Architecture & Deployment Guide

This is a professional medical diagnostic system.

## 🏗 System Architecture
- **Frontend**: Next.js (App Router) + Tailwind CSS + ShadCN UI
- **Storage**: Firebase Storage (Secure Medical Imaging)
- **Database**: Firestore (Diagnostic Results & Patient History)
- **Functions**: Firebase Functions (Node.js) to bridge UI and AI engine
- **AI Engine**: FastAPI + PyTorch CNN (Deployed on Google Cloud Run)

## 📁 Folder Structure
- `src/app`: Next.js frontend pages
- `src/components`: Reusable UI components
- `src/lib`: Configuration (Firebase, Utils)
- `src/ai-backend`: Python FastAPI and PyTorch code

## 🚀 Deployment Steps
1. **Firebase Setup**:
   - `firebase init hosting firestore storage functions`
   - Set up Firebase Authentication (Email/Password)

2. **AI Backend (Google Cloud Run)**:
   - `cd src/ai-backend`
   - `docker build -t gcr.io/[PROJECT-ID]/disease-ai-engine .`
   - `docker push gcr.io/[PROJECT-ID]/disease-ai-engine`
   - Deploy to Cloud Run: `gcloud run deploy --image gcr.io/[PROJECT-ID]/disease-ai-engine`

3. **Connecting Firebase to AI Engine**:
   - In Firebase Functions, call the Cloud Run URL using `axios` or `node-fetch`.
   - Pass the Storage image URL to the FastAPI endpoint.
   - Save the returned JSON result into Firestore under the user's `history` collection.

4. **Frontend**:
   - `npm run build`
   - `firebase deploy --only hosting`
