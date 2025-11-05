import React from 'react';

import Navbar from './components/Navbar';

// Navbar Component
<Navbar />

// Home Page Component

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#071026] via-[#071428] to-[#0b1724] text-white flex flex-col">
      <Navbar />

      {/* HERO */}
      <main className="flex-1 flex items-center">
        <div className="max-w-7xl mx-auto w-full px-6 py-20">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            {/* Left Column */}
            <div>
              <div className="inline-flex items-center gap-2 bg-white/5 backdrop-blur-sm text-slate-200 rounded-full px-4 py-2 text-sm mb-8 border border-white/10">
                <svg className="w-4 h-4 text-indigo-400" viewBox="0 0 24 24" fill="none">
                  <path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <span>Private • Secure • Page-cited answers</span>
              </div>

              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold leading-tight mb-6 bg-gradient-to-r from-white via-slate-100 to-slate-300 bg-clip-text text-transparent">
                Ask your book anything
              </h1>

              <p className="text-xl text-slate-300 leading-relaxed mb-10 max-w-xl">
                Upload any PDF and get instant answers with exact page citations. Perfect for students, researchers, and professionals who need accurate information fast.
              </p>

              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 mb-12">
                <a
                  href="/upload"
                  className="group inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-indigo-500 to-violet-600 px-8 py-4 text-base font-semibold shadow-xl hover:shadow-indigo-500/50 transition-all hover:scale-105"
                >
                  <span>Upload PDF — Try Free</span>
                  <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </a>
                <a href="#features" className="text-base text-slate-300 hover:text-white flex items-center gap-2 transition-colors">
                  <span>See how it works</span>
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </a>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-6">
                <div>
                  <div className="text-3xl font-bold text-indigo-400 mb-1">100%</div>
                  <div className="text-sm text-slate-400">Accurate Citations</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-violet-400 mb-1">&lt;5s</div>
                  <div className="text-sm text-slate-400">Average Response</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-purple-400 mb-1">500+</div>
                  <div className="text-sm text-slate-400">Pages Indexed</div>
                </div>
              </div>
            </div>

            {/* Right Column - Feature Cards */}
            <div className="flex flex-col gap-6">
              {/* Main Feature Card */}
              <div className="p-8 rounded-2xl bg-gradient-to-br from-indigo-500/10 to-violet-500/10 border border-white/10 backdrop-blur-sm shadow-2xl">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center mb-4">
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold mb-3">AI-Powered Q&A</h3>
                <p className="text-slate-300 leading-relaxed mb-6">
                  Ask questions in natural language and get precise answers extracted from your documents, complete with page numbers and context.
                </p>
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <svg className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-sm text-slate-300">No hallucinations — answers from your text only</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <svg className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-sm text-slate-300">Page-level citations for easy verification</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <svg className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-sm text-slate-300">Optimized for large documents up to 500 pages</span>
                  </div>
                </div>
              </div>

              {/* Secondary Cards */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-6 rounded-xl bg-white/5 border border-white/10 backdrop-blur-sm hover:bg-white/10 transition-colors">
                  <div className="w-10 h-10 rounded-lg bg-indigo-500/20 flex items-center justify-center mb-3">
                    <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  </div>
                  <h4 className="font-semibold mb-2">Private & Secure</h4>
                  <p className="text-xs text-slate-400">Your documents stay private and are never used for training</p>
                </div>
                <div className="p-6 rounded-xl bg-white/5 border border-white/10 backdrop-blur-sm hover:bg-white/10 transition-colors">
                  <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center mb-3">
                    <svg className="w-5 h-5 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <h4 className="font-semibold mb-2">Lightning Fast</h4>
                  <p className="text-xs text-slate-400">Get answers in seconds with our optimized search engine</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Subtle background decoration */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/4 -left-40 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 -right-40 w-96 h-96 bg-violet-500/10 rounded-full blur-3xl"></div>
      </div>
    </div>
  );
}