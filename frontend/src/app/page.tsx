"use client";
import { useState, useEffect } from 'react';
// FIX: Changed to relative imports to avoid alias resolution errors
import Navbar from '../components/Navbar';
import FileUpload from '../components/FileUpload';
import StatusIndicator from '../components/StatusIndicator';
import ChatInterface from '../components/ChatInterface';
import { api } from '../lib/api';

export default function Home() {
  const [uploadId, setUploadId] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'processing' | 'completed' | 'failed'>('idle');

  const handleUploadSuccess = (id: string, name: string) => {
    setUploadId(id);
    setFileName(name);
    setStatus('completed');
  };

  const handleReset = async () => {
    if (uploadId) await api.clearSession(uploadId).catch(console.error);
    setUploadId(null);
    setFileName(null);
    setStatus('idle');
  };

  // FIX: Use 'beforeunload' for reliable cleanup on refresh/close
  useEffect(() => {
    const handleBeforeUnload = () => {
      if (uploadId) {
        // 1. Get API URL safely
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        
        // 2. Prepare data (Beacon sends POST requests)
        const blob = new Blob([JSON.stringify({})], { type: 'application/json' });
        
        // 3. Fire and forget
        navigator.sendBeacon(`${baseUrl}/api/clear/${uploadId}`, blob);
      }
    };

    // Attach listener
    window.addEventListener('beforeunload', handleBeforeUnload);

    // Cleanup listener
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [uploadId]);

  return (
    <main className="min-h-screen bg-slate-50 selection:bg-indigo-100 selection:text-indigo-900 pb-20">
      <Navbar />

      <div className="max-w-5xl mx-auto px-4 py-16 sm:px-6 lg:px-8">
        
        {/* Hero Section */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-6 animate-in">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white border border-slate-200 shadow-sm text-xs font-medium text-slate-600 mb-4">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
            </span>
            Powered by Gemini 2.5 Flash
          </div>
          
          <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-slate-900 leading-[1.1]">
            Chat with your <br/>
            <span className="text-indigo-600">Documents</span>
          </h1>
          
          <p className="text-lg md:text-xl text-slate-600 leading-relaxed max-w-2xl mx-auto">
            Transform any PDF into an interactive knowledge base. 
            Ask questions, get summaries, and find citations instantly.
          </p>
        </div>

        {/* App Container */}
        <div className="bg-white rounded-2xl shadow-xl shadow-slate-200/60 border border-slate-200 overflow-hidden transition-all duration-500 min-h-[500px] flex flex-col">
          
          {/* App Toolbar */}
          {(status !== 'idle' || fileName) && (
            <div className="border-b border-slate-100 bg-slate-50/80 px-6 py-4 flex items-center justify-between backdrop-blur-sm sticky top-0 z-10">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-white rounded-lg shadow-sm border border-slate-200 flex items-center justify-center">
                  <svg className="w-6 h-6 text-red-500" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M7 2v2h10V2h2v2h1a2 2 0 012 2v14a2 2 0 01-2 2H4a2 2 0 01-2-2V6a2 2 0 012-2h1V2h2zm0 4v14h10V6H7zm2 2h6v2H9V8zm0 4h6v2H9v-2zm0 4h6v2H9v-2z"/>
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-900 truncate max-w-[200px]">
                    {fileName || 'Processing File...'}
                  </p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <StatusIndicator status={status} />
                    <span className="text-xs text-slate-400">•</span>
                    <span className="text-xs text-slate-500 uppercase tracking-wider font-medium">PDF</span>
                  </div>
                </div>
              </div>

              {status === 'completed' && (
                <button 
                  onClick={handleReset}
                  className="text-xs font-medium text-slate-500 hover:text-red-600 hover:bg-red-50 px-3 py-1.5 rounded-md transition-colors border border-transparent hover:border-red-100"
                >
                  Upload New File
                </button>
              )}
            </div>
          )}

          {/* Content Area */}
          <div className="flex-1 bg-slate-50/30 relative">
            {status === 'completed' && uploadId ? (
              <div className="h-[600px] animate-in fade-in slide-in-from-bottom-4 duration-500">
                <ChatInterface uploadId={uploadId} />
              </div>
            ) : (
              <div className="h-[500px] flex flex-col items-center justify-center p-8 animate-in zoom-in-95 duration-500">
                <div className="w-full max-w-xl">
                  <FileUpload 
                    onUploadSuccess={handleUploadSuccess} 
                    onStatusChange={setStatus} 
                  />
                  
                  {/* Feature Badges */}
                  <div className="mt-12 grid grid-cols-3 gap-6 opacity-60 grayscale hover:grayscale-0 transition-all duration-500">
                    {[
                      { label: 'Fast Analysis', icon: '⚡' },
                      { label: 'Secure & Private', icon: '🔒' },
                      { label: 'Smart Citations', icon: '📚' },
                    ].map((f, i) => (
                      <div key={i} className="flex flex-col items-center gap-2 text-center group">
                        <div className="w-10 h-10 rounded-full bg-indigo-50 flex items-center justify-center text-xl mb-1 group-hover:scale-110 transition-transform">
                          {f.icon}
                        </div>
                        <span className="text-xs font-semibold text-slate-600">{f.label}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}