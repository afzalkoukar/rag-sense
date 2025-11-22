"use client";
import { useState, useCallback } from 'react';
import { api } from '@/lib/api';

interface FileUploadProps {
  onUploadSuccess: (uploadId: string, fileName: string) => void;
  onStatusChange: (status: 'idle' | 'uploading' | 'processing' | 'completed' | 'failed') => void;
}

export default function FileUpload({ onUploadSuccess, onStatusChange }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);

  const processFile = async (file: File) => {
    if (file.type !== 'application/pdf') {
      alert('Please upload a PDF file.');
      return;
    }

    try {
      onStatusChange('uploading');
      const response = await api.uploadFile(file);
      if (response.data) {
        const { upload_id, file_name } = response.data;
        onStatusChange('processing');
        pollStatus(upload_id, file_name);
      }
    } catch (error) {
      console.error(error);
      onStatusChange('failed');
    }
  };

  const pollStatus = async (uploadId: string, fileName: string) => {
    const interval = setInterval(async () => {
      try {
        const statusRes = await api.checkStatus(uploadId);
        if (statusRes.data?.status === 'completed') {
          clearInterval(interval);
          onStatusChange('completed');
          onUploadSuccess(uploadId, fileName);
        } else if (statusRes.data?.status === 'failed') {
          clearInterval(interval);
          onStatusChange('failed');
        }
      } catch (e) {
        clearInterval(interval);
        onStatusChange('failed');
      }
    }, 2000);
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setIsDragging(true);
    else if (e.type === 'dragleave') setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  }, []);

  return (
    <div className="relative">
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`
          group relative w-full rounded-2xl border-2 border-dashed transition-all duration-300 ease-out
          flex flex-col items-center justify-center cursor-pointer overflow-hidden
          ${isDragging 
            ? 'border-indigo-500 bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 scale-[1.02] shadow-2xl shadow-indigo-500/20' 
            : 'border-slate-300 bg-gradient-to-br from-white to-slate-50 hover:border-indigo-400 hover:shadow-xl hover:scale-[1.01]'}
        `}
        style={{ minHeight: '280px' }}
      >
        <input 
          type="file" 
          accept=".pdf" 
          className="hidden" 
          id="file-input"
          onChange={(e) => e.target.files?.[0] && processFile(e.target.files[0])}
        />
        
        <label htmlFor="file-input" className="w-full h-full flex flex-col items-center justify-center cursor-pointer z-10 py-12 px-6">
          
          {/* Icon Container */}
          <div className="relative mb-6">
            {/* Glow effect */}
            <div className={`
              absolute inset-0 rounded-full blur-xl transition-all duration-300
              ${isDragging 
                ? 'bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 opacity-40 scale-110' 
                : 'bg-gradient-to-r from-indigo-300 to-purple-300 opacity-0 group-hover:opacity-30 group-hover:scale-110'}
            `}></div>
            
            {/* Icon circle */}
            <div className={`
              relative p-6 rounded-2xl transition-all duration-300 shadow-lg
              ${isDragging 
                ? 'bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 scale-110 rotate-6' 
                : 'bg-gradient-to-br from-indigo-100 to-purple-100 group-hover:from-indigo-200 group-hover:to-purple-200 group-hover:scale-110 group-hover:-rotate-3'}
            `}>
              <svg 
                className={`w-12 h-12 transition-colors duration-300 ${isDragging ? 'text-white' : 'text-indigo-600'}`} 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
          </div>

          {/* Text Content */}
          <div className="text-center space-y-2 max-w-sm">
            <p className={`text-xl font-bold transition-all duration-300 ${
              isDragging 
                ? 'text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 scale-105' 
                : 'text-slate-700 group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-indigo-600 group-hover:to-purple-600'
            }`}>
              {isDragging ? "Drop your PDF here" : "Upload your PDF document"}
            </p>
            <p className="text-sm text-slate-500 font-medium">
              Click to browse or drag and drop your file
            </p>
            <div className="flex items-center justify-center gap-2 pt-2">
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-slate-100 text-xs font-medium text-slate-600">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                PDF Only
              </span>
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-slate-100 text-xs font-medium text-slate-600">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Max 10MB
              </span>
            </div>
          </div>
        </label>

        {/* Animated background pattern */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          <div className={`
            absolute inset-0 transition-opacity duration-300
            ${isDragging ? 'opacity-10' : 'opacity-5'}
            bg-[radial-gradient(circle_at_50%_120%,rgba(99,102,241,0.3),rgba(168,85,247,0.3),rgba(236,72,153,0.3))]
          `}></div>
          <div className="absolute inset-0 bg-[radial-gradient(#4f46e5_1px,transparent_1px)] [background-size:20px_20px] opacity-[0.03]"></div>
        </div>

        {/* Corner decorations */}
        <div className={`absolute top-4 right-4 w-16 h-16 rounded-full bg-gradient-to-br from-indigo-200 to-purple-200 blur-2xl transition-opacity duration-300 ${isDragging ? 'opacity-60' : 'opacity-0 group-hover:opacity-40'}`}></div>
        <div className={`absolute bottom-4 left-4 w-20 h-20 rounded-full bg-gradient-to-br from-purple-200 to-pink-200 blur-2xl transition-opacity duration-300 ${isDragging ? 'opacity-60' : 'opacity-0 group-hover:opacity-40'}`}></div>
      </div>
    </div>
  );
}