# **App Name**: Disease AI System

## Core Features:

- Secure User Authentication: Enables users to securely sign up, log in, and manage their sessions, ensuring privacy and personalized access to diagnostic data. Uses Firebase Authentication.
- Medical Image Upload: Provides an intuitive interface for users to upload medical images (e.g., X-rays, CT scans) directly from their device. Images are securely stored and managed by Firebase Storage.
- AI Diagnostic Engine: Utilizes a custom PyTorch CNN model, deployed as a FastAPI server on Google Cloud Run, to analyze uploaded medical images and provide disease predictions. Firebase Functions orchestrate the image processing and communicate with this external AI tool.
- Personalized Diagnostic History: A user-friendly dashboard displaying a comprehensive history of all uploaded images, their corresponding AI prediction results, and relevant metadata, all securely persisted in Firestore.

## Style Guidelines:

- The chosen light color scheme conveys a sense of clinical purity, trustworthiness, and forward-thinking professionalism, apt for an early disease diagnosis system.
- Primary brand color: A refined and dependable blue, '#2258C3' (RGB 34, 88, 195), evokes clarity and confidence, perfectly balancing technological advancement with medical care.
- Background color: A very subtle and light blue-grey, '#F0F2F4' (RGB 240, 242, 244), offering a clean and unobtrusive canvas that highlights content without visual fatigue.
- Accent color: A crisp and luminous cyan, '#5ED5ED' (RGB 94, 213, 237), designed to draw attention to critical calls-to-action, alerts, and key interactive elements, signifying progress and vitality.
- Headlines and Body text font: 'Inter' (sans-serif) for its modern, highly legible, and objective aesthetic, ensuring clear communication of diagnostic information and a seamless user experience across all text elements.
- Clean, contemporary line-art icons will be used throughout the application to maintain a minimalist and professional look, supporting quick comprehension of functions such as upload, history, and results. Icons will maintain a consistent visual weight and style.
- A responsive, minimalist dashboard layout focused on content hierarchy. Ample whitespace will ensure clarity and reduce cognitive load. Key information such as diagnosis results and history will be prominently displayed and easily accessible, designed for optimal viewing on various devices.
- Subtle and functional micro-animations will be employed to enhance user feedback and perception of responsiveness, particularly during image uploads, processing states, and result presentations. Animations will be smooth, non-distracting, and indicate system activity without lengthy waits.