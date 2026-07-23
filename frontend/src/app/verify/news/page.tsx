'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Search, ArrowLeft, Loader2, Info } from 'lucide-react';
import Link from 'next/link';
import { api } from '@/lib/api';

const LOADING_STAGES = [
  "Consulting Global Fact-Checking Archives...",
  "Querying NewsAPI for widespread media coverage...",
  "Querying MediaStack news data feeds...",
  "Aggregating timeline logs from GDELT indexes...",
  "Running Trust Engine weighting algorithms...",
  "Prompting Groq LLaMA-3.1 fact reasoning engine..."
];

export default function VerifyNewsPage() {
  const router = useRouter();
  const [claim, setClaim] = useState('');
  const [loading, setLoading] = useState(false);
  const [stageIndex, setStageIndex] = useState(0);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!claim.trim()) return;

    setLoading(true);
    setError('');
    setStageIndex(0);

    // Cycle through loading stages every 2.5 seconds
    const interval = setInterval(() => {
      setStageIndex((prev) => (prev < LOADING_STAGES.length - 1 ? prev + 1 : prev));
    }, 2500);

    try {
      const res = await api.post<{ id: string }>('/verify/news', { claim });
      clearInterval(interval);
      // Redirect to the shareable report page
      router.push(`/report/${res.id}`);
    } catch (err: any) {
      clearInterval(interval);
      setError(err.message || 'Verification failed. Please try again.');
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#030712] text-white flex flex-col justify-center items-center px-4 relative overflow-hidden">
      
      {/* Background decorations */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Navigation */}
      <div className="absolute top-8 left-8">
        <Link href="/dashboard" className="flex items-center gap-2 text-sm text-white/50 hover:text-white transition-colors">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </Link>
      </div>

      <div className="w-full max-w-2xl">
        <AnimatePresence mode="wait">
          {!loading ? (
            <motion.div
              key="input-form"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.4 }}
              className="space-y-8"
            >
              <div className="text-center space-y-3">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 mb-2">
                  <Search className="w-6 h-6" />
                </div>
                <h1 className="text-3xl font-extrabold tracking-tight">Verify News Claims</h1>
                <p className="text-white/50 text-sm max-w-md mx-auto">
                  Paste a news headline, quote, or claim to evaluate credibility across multiple fact databases and AI algorithms.
                </p>
              </div>

              <div className="glass-card p-6 border border-white/10 bg-white/5 backdrop-blur-md rounded-2xl">
                <form onSubmit={handleSubmit} className="space-y-4">
                  {error && (
                    <div className="p-3 text-xs bg-red-500/10 border border-red-500/20 rounded-lg text-red-400">
                      {error}
                    </div>
                  )}

                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-white/70 uppercase tracking-wider block">News claim / URL</label>
                    <textarea
                      required
                      rows={4}
                      placeholder="e.g., NASA confirmed alien spaceships have landed in Area 51."
                      value={claim}
                      onChange={(e) => setClaim(e.target.value)}
                      className="w-full p-4 rounded-xl bg-white/5 border border-white/10 focus:border-emerald-500/50 focus:bg-white/10 focus:outline-none transition-all text-sm text-white resize-none"
                    />
                  </div>

                  <button
                    type="submit"
                    className="w-full py-4 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold text-sm transition-all shadow-lg shadow-emerald-500/25 flex items-center justify-center gap-2 cursor-pointer"
                  >
                    <span>Analyze Authenticity</span>
                    <Search className="w-4 h-4" />
                  </button>
                </form>
              </div>

              <div className="p-4 rounded-xl border border-white/5 bg-white/[0.01] flex items-start gap-3 max-w-xl mx-auto">
                <Info className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                <p className="text-[11px] leading-relaxed text-white/45">
                  TruthLens queries the Google Fact Check Database, GDELT indexing protocols, and global media outlets. In parallel, a LLaMA LLM completes contextual logic verification. Reports are permanently saved and shareable.
                </p>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="loading-state"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.4 }}
              className="glass-card p-12 border border-white/10 bg-white/5 rounded-3xl text-center space-y-8 flex flex-col items-center"
            >
              <div className="relative w-24 h-24 flex items-center justify-center">
                <div className="absolute inset-0 rounded-full border-4 border-white/5 border-t-emerald-400 animate-spin" />
                <Shield className="w-8 h-8 text-emerald-400 animate-pulse" />
              </div>

              <div className="space-y-2">
                <h3 className="text-xl font-bold tracking-tight text-white">TruthLens Verification Pipeline Active</h3>
                <p className="text-xs text-white/40">Gathering indexes from 7 real-time resources...</p>
              </div>

              {/* Progress Stage Text */}
              <div className="py-2.5 px-6 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-semibold animate-pulse">
                {LOADING_STAGES[stageIndex]}
              </div>

              {/* Mock indicators */}
              <div className="text-[10px] text-white/30 tracking-wide">
                This may take a few seconds. Do not refresh or exit.
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </main>
  );
}
