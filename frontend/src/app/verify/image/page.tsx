'use client';

import React, { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, ImageIcon, ArrowLeft, Loader2, Upload, X, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import { api } from '@/lib/api';

const LOADING_STAGES = [
  "Uploading image binaries...",
  "Querying Hive Moderation deepfake detection engine...",
  "Querying Google Vision API annotations...",
  "Running SafeSearch content safety evaluations...",
  "Scanning web visual repositories for exact matches...",
  "Running Trust Engine weighting algorithms...",
  "Executing Groq LLaMA-3.1 image evaluation reasoning..."
];

export default function VerifyImagePage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [stageIndex, setStageIndex] = useState(0);
  const [error, setError] = useState('');

  const handleFileChange = (selectedFile: File) => {
    if (!selectedFile.type.startsWith('image/')) {
      setError('Please select an image file (PNG, JPG, WEBP).');
      return;
    }
    setError('');
    setFile(selectedFile);
    
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(selectedFile);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const clearSelection = () => {
    setFile(null);
    setPreview('');
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError('');
    setStageIndex(0);

    const interval = setInterval(() => {
      setStageIndex((prev) => (prev < LOADING_STAGES.length - 1 ? prev + 1 : prev));
    }, 2500);

    try {
      const res = await api.postFile<{ id: string }>('/verify/image', file);
      clearInterval(interval);
      router.push(`/report/${res.id}`);
    } catch (err: any) {
      clearInterval(interval);
      setError(err.message || 'Image verification failed.');
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
                  <ImageIcon className="w-6 h-6" />
                </div>
                <h1 className="text-3xl font-extrabold tracking-tight">Verify Image Authenticity</h1>
                <p className="text-white/50 text-sm max-w-md mx-auto">
                  Upload any picture to detect deepfakes, AI generations, metadata modifications, or web discrepancies.
                </p>
              </div>

              <div className="glass-card p-6 border border-white/10 bg-white/5 backdrop-blur-md rounded-2xl">
                <form onSubmit={handleSubmit} className="space-y-6">
                  {error && (
                    <div className="p-3 text-xs bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 flex-shrink-0" />
                      <span>{error}</span>
                    </div>
                  )}

                  {!preview ? (
                    <div
                      onDragOver={handleDragOver}
                      onDrop={handleDrop}
                      onClick={() => fileInputRef.current?.click()}
                      className="border-2 border-dashed border-white/10 hover:border-emerald-500/50 rounded-2xl p-12 text-center flex flex-col items-center justify-center gap-4 cursor-pointer transition-colors bg-white/[0.01] hover:bg-white/[0.03]"
                    >
                      <Upload className="w-10 h-10 text-white/30" />
                      <div>
                        <p className="text-sm font-semibold">Drag &amp; drop an image here</p>
                        <p className="text-xs text-white/40 mt-1">or click to browse from files</p>
                      </div>
                      <p className="text-[10px] text-white/30 uppercase tracking-widest">Supports PNG, JPG, WEBP</p>
                      <input
                        type="file"
                        ref={fileInputRef}
                        onChange={(e) => e.target.files?.[0] && handleFileChange(e.target.files[0])}
                        accept="image/*"
                        className="hidden"
                      />
                    </div>
                  ) : (
                    <div className="relative rounded-2xl overflow-hidden border border-white/10 bg-black/40">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={preview} alt="Upload preview" className="max-h-[300px] w-full object-contain mx-auto" />
                      <button
                        type="button"
                        onClick={clearSelection}
                        className="absolute top-3 right-3 p-1.5 rounded-full bg-black/60 border border-white/10 text-white hover:bg-black transition-colors cursor-pointer"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={!file}
                    className="w-full py-4 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold text-sm transition-all shadow-lg shadow-emerald-500/25 flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span>Analyze Image</span>
                    <ImageIcon className="w-4 h-4" />
                  </button>
                </form>
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
                <h3 className="text-xl font-bold tracking-tight text-white">TruthLens Image Pipeline Active</h3>
                <p className="text-xs text-white/40">Running safe checks and deepfake audits...</p>
              </div>

              {/* Progress Stage Text */}
              <div className="py-2.5 px-6 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-semibold animate-pulse">
                {LOADING_STAGES[stageIndex]}
              </div>

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
