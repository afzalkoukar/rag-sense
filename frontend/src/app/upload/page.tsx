'use client';

import React, { useState } from 'react';
import Navbar from '@/app/components/Navbar';

// Navbar Component
<Navbar />

// Upload Page Component

export default function UploadPage() {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
      handleFile(file);
    }
  };

  const handleFileInput = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFile(file);
    }
  };

  const handleFile = (file) => {
    setUploadedFile(file);
    setIsProcessing(true);
    
    // Simulate processing
    setTimeout(() => {
      setIsProcessing(false);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#071026] via-[#071428] to-[#0b1724] text-white flex flex-col">
      <Navbar />

      <main className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="max-w-2xl w-full">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4">Upload Your PDF</h1>
            <p className="text-slate-300 text-lg">
              Drop your file below to start asking questions
            </p>
          </div>

          {/* Upload Area */}
          {!uploadedFile ? (
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all ${
                isDragging
                  ? 'border-indigo-500 bg-indigo-500/10'
                  : 'border-white/20 bg-white/5'
              }`}
            >
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileInput}
                className="hidden"
                id="file-upload"
              />
              
              <div className="flex flex-col items-center gap-6">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
                  <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>

                <div>
                  <p className="text-xl font-semibold mb-2">
                    Drag and drop your PDF here
                  </p>
                  <p className="text-slate-400 text-sm">or</p>
                </div>

                <label
                  htmlFor="file-upload"
                  className="cursor-pointer inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-indigo-500 to-violet-600 px-8 py-3 text-base font-semibold shadow-lg hover:shadow-indigo-500/50 transition-all hover:scale-105"
                >
                  Browse Files
                </label>

                <p className="text-sm text-slate-400">
                  Supports PDF files up to 50MB
                </p>
              </div>
            </div>
          ) : (
            <div className="border border-white/20 rounded-2xl p-8 bg-white/5">
              {isProcessing ? (
                <div className="text-center">
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center mx-auto mb-6 animate-pulse">
                    <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Processing your PDF...</h3>
                  <p className="text-slate-400">This may take a few moments</p>
                </div>
              ) : (
                <div>
                  <div className="flex items-center gap-4 mb-6">
                    <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center flex-shrink-0">
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg">{uploadedFile.name}</h3>
                      <p className="text-sm text-slate-400">
                        {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                    <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                      <svg className="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <a
                      href="/chat"
                      className="flex-1 text-center rounded-full bg-gradient-to-r from-indigo-500 to-violet-600 px-6 py-3 font-semibold shadow-lg hover:shadow-indigo-500/50 transition-all hover:scale-105"
                    >
                      Start Asking Questions
                    </a>
                    <button
                      onClick={() => setUploadedFile(null)}
                      className="px-6 py-3 rounded-full bg-white/10 hover:bg-white/20 transition-colors font-medium"
                    >
                      Upload New
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Features */}
          <div className="grid grid-cols-3 gap-4 mt-12">
            <div className="text-center p-4">
              <div className="w-10 h-10 rounded-lg bg-indigo-500/20 flex items-center justify-center mx-auto mb-3">
                <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <p className="text-sm text-slate-300">100% Private</p>
            </div>
            <div className="text-center p-4">
              <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center mx-auto mb-3">
                <svg className="w-5 h-5 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <p className="text-sm text-slate-300">Fast Processing</p>
            </div>
            <div className="text-center p-4">
              <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center mx-auto mb-3">
                <svg className="w-5 h-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <p className="text-sm text-slate-300">Accurate Citations</p>
            </div>
          </div>
        </div>
      </main>

      {/* Background decoration */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden -z-10">
        <div className="absolute top-1/4 -left-40 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 -right-40 w-96 h-96 bg-violet-500/10 rounded-full blur-3xl"></div>
      </div>
    </div>
  );
}