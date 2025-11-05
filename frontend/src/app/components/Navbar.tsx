"use client";

import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="border-b border-white/10 backdrop-blur-sm bg-black/20">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
            <span className="text-white font-bold text-lg">B</span>
          </div>
          <span className="text-xl font-bold">BookQ</span>
        </div>
        <div className="hidden md:flex items-center gap-8">
          <a href="#features" className="text-sm text-slate-300 hover:text-white transition-colors">Features</a>
          <a href="#how-it-works" className="text-sm text-slate-300 hover:text-white transition-colors">How it Works</a>
          <a href="#pricing" className="text-sm text-slate-300 hover:text-white transition-colors">Pricing</a>
        </div>
      </div>
    </nav>
  );
}