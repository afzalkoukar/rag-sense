# DocuMind Frontend

The user interface for DocuMind, built with Next.js 14 (App Router) and styled with Tailwind CSS. It features a modern, responsive design with upload capabilities and a chat interface.

## 🎨 Features

* **Drag & Drop Upload**: Easy file ingestion.
* **Real-time Status**: Polling for backend processing status.
* **Chat Interface**: Clean, message-bubble UI with citations.
* **Session Management**: Automatic cleanup when leaving the page.

## 🛠️ Setup & Installation

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Variables

Create a `.env.local` file in the `frontend` directory:

```env
# URL of your Backend API (No trailing slash)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

The app will be available at: **http://localhost:3000**

## 📂 Project Structure

```
src/
├── app/
│   ├── globals.css      # Global styles
│   ├── layout.tsx       # Root layout
│   └── page.tsx         # Main logic (State machine)
├── components/
│   ├── ChatInterface.tsx
│   ├── FileUpload.tsx
│   ├── MessageBubble.tsx
│   ├── Navbar.tsx
│   └── StatusIndicator.tsx
└── lib/
    └── api.ts           # API Client
```

## 🚀 Deployment

This project is optimized for deployment on Vercel.

1. Push code to GitHub.
2. Import project into Vercel.
3. Add the `NEXT_PUBLIC_API_URL` environment variable (pointing to your hosted backend).
4. Deploy!