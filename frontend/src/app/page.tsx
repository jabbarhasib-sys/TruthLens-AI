'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { TubesBackground } from '@/components/ui/neon-flow';
import {
  Shield,
  Search,
  ImageIcon,
  Zap,
  CheckCircle,
  ArrowRight,
  ExternalLink,
  MousePointer2,
  BarChart3,
  Globe,
  Brain,
} from 'lucide-react';
import Link from 'next/link';

// ─── Animation Variants ───────────────────────────────────────────────────────
const fadeUp = {
  hidden: { opacity: 0, y: 40 },
  visible: (i: number = 0) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.7, delay: i * 0.12, ease: 'easeOut' as const },
  }),
};


const stagger = {
  visible: { transition: { staggerChildren: 0.1 } },
};

// ─── Feature Card ─────────────────────────────────────────────────────────────
function FeatureCard({
  icon: Icon,
  title,
  description,
  delay,
}: {
  icon: React.ElementType;
  title: string;
  description: string;
  delay: number;
}) {
  return (
    <motion.div
      variants={fadeUp}
      custom={delay}
      className="group relative rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm p-6 hover:border-emerald-500/50 hover:bg-white/8 transition-all duration-300"
    >
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-emerald-500/5 to-teal-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      <div className="relative">
        <div className="mb-4 inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 border border-emerald-500/30">
          <Icon className="w-6 h-6 text-emerald-400" />
        </div>
        <h3 className="mb-2 text-lg font-semibold text-white">{title}</h3>
        <p className="text-sm text-white/60 leading-relaxed">{description}</p>
      </div>
    </motion.div>
  );
}

// ─── Stat Card ────────────────────────────────────────────────────────────────
function StatCard({
  value,
  label,
  delay,
}: {
  value: string;
  label: string;
  delay: number;
}) {
  return (
    <motion.div variants={fadeUp} custom={delay} className="text-center">
      <div className="text-4xl font-bold bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">
        {value}
      </div>
      <div className="mt-1 text-sm text-white/50">{label}</div>
    </motion.div>
  );
}

// ─── How It Works Step ────────────────────────────────────────────────────────
function StepCard({
  number,
  title,
  description,
  delay,
}: {
  number: string;
  title: string;
  description: string;
  delay: number;
}) {
  return (
    <motion.div
      variants={fadeUp}
      custom={delay}
      className="relative flex flex-col items-center text-center"
    >
      <div className="mb-4 flex items-center justify-center w-14 h-14 rounded-full bg-gradient-to-br from-emerald-600 to-teal-600 text-white font-bold text-xl shadow-lg shadow-emerald-500/30">
        {number}
      </div>
      <h3 className="mb-2 text-lg font-semibold text-white">{title}</h3>
      <p className="text-sm text-white/55 leading-relaxed max-w-xs">{description}</p>
    </motion.div>
  );
}

// ─── Navbar ───────────────────────────────────────────────────────────────────
function Navbar() {
  return (
    <motion.nav
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="absolute top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-5 md:px-12 pointer-events-auto"
    >
      {/* Logo */}
      <div className="flex items-center gap-2">
        <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500">
          <Shield className="w-4 h-4 text-white" />
        </div>
        <span className="text-lg font-bold tracking-tight text-white">
          Truth<span className="text-emerald-400">Lens</span>{' '}
          <span className="text-xs font-medium text-white/40">AI</span>
        </span>
      </div>

      {/* Nav Links */}
      <div className="hidden md:flex items-center gap-8 text-sm text-white/60">
        <a href="#features" className="hover:text-white transition-colors">Features</a>
        <a href="#how-it-works" className="hover:text-white transition-colors">How it works</a>
        <a href="#accuracy" className="hover:text-white transition-colors">Accuracy</a>
      </div>

      {/* CTA */}
      <div className="flex items-center gap-3">
        <Link
          href="/login"
          className="hidden md:block text-sm text-white/60 hover:text-white transition-colors"
        >
          Sign in
        </Link>
        <Link
          href="/dashboard"
          className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-full bg-gradient-to-r from-emerald-600 to-teal-600 text-white hover:from-emerald-500 hover:to-teal-500 transition-all duration-200 shadow-lg shadow-emerald-500/25"
        >
          Get started <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </motion.nav>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────
export default function LandingPage() {
  return (
    <main className="min-h-screen bg-[#030712] text-white">
      {/* ── HERO with Neon Flow ──────────────────────────────────────────── */}
      <section className="relative w-full h-screen">
        <TubesBackground className="bg-[#030712]" enableClickInteraction>
          <Navbar />

          {/* Hero Content */}
          <div className="pointer-events-auto flex flex-col items-center justify-center w-full h-full text-center px-4 gap-6">
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="inline-flex items-center gap-2 px-5 py-2 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-sm font-medium uppercase tracking-widest"
            >
              <Zap className="w-4 h-4" />
              AI-Powered Real-Time Verification
            </motion.div>

            {/* Headline */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.35 }}
              className="space-y-5"
            >
              <h1
                className="font-extrabold tracking-tighter leading-none select-none whitespace-nowrap"
                style={{
                  fontSize: 'clamp(3rem, 13vw, 16rem)',
                  textShadow: '0 0 80px rgba(16,185,129,0.6), 0 0 160px rgba(16,185,129,0.25)',
                }}
              >
                <span className="text-white">Truth</span>
                <span
                  style={{
                    color: '#00ff88',
                    WebkitTextStroke: '2px #00ff88',
                    textShadow:
                      '0 0 10px #00ff88, 0 0 30px #00ff88, 0 0 60px #00cc66, 0 0 100px #00aa44',
                  }}
                >
                  Lens
                </span>
                <span className="text-white/80"> AI</span>
              </h1>
              <p className="text-xl md:text-2xl lg:text-3xl font-light text-white/55 max-w-3xl mx-auto leading-relaxed">
                Verify news &amp; images instantly with multi-source AI fact-checking.
                <br className="hidden md:block" />
                <span className="text-white/80 font-normal"> Know what&apos;s real.</span>
              </p>
            </motion.div>

            {/* CTA Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.55 }}
              className="flex flex-col sm:flex-row items-center gap-4"
            >
              <Link
                href="/verify/news"
                className="group flex items-center gap-2.5 px-10 py-4 rounded-full bg-gradient-to-r from-emerald-600 to-teal-600 text-white font-semibold text-base hover:from-emerald-500 hover:to-teal-500 transition-all duration-200 shadow-2xl shadow-emerald-500/40 hover:shadow-emerald-500/60 hover:-translate-y-0.5"
              >
                <Search className="w-5 h-5" />
                Verify News
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                href="/verify/image"
                className="flex items-center gap-2.5 px-10 py-4 rounded-full border border-white/20 text-white/80 font-semibold text-base hover:border-white/40 hover:text-white hover:bg-white/5 transition-all duration-200"
              >
                <ImageIcon className="w-5 h-5" />
                Analyse Image
              </Link>
            </motion.div>

            {/* Trust indicators */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.7, delay: 0.75 }}
              className="flex flex-wrap justify-center items-center gap-4 sm:gap-8 text-sm text-white/45"
            >
              {['Google Fact Check', 'GDELT', 'Groq AI', 'NewsAPI'].map((s) => (
                <span key={s} className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-emerald-400" />
                  {s}
                </span>
              ))}
            </motion.div>
          </div>

          {/* Bottom hint */}
          <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-white/30 animate-pulse pointer-events-none">
            <MousePointer2 className="w-4 h-4" />
            <span className="text-[10px] uppercase tracking-widest">Click to randomize colors</span>
          </div>
        </TubesBackground>
      </section>

      {/* ── STATS BAND ──────────────────────────────────────────────────── */}
      <section className="relative border-y border-white/10 bg-white/[0.02] py-14">
        <div className="max-w-4xl mx-auto px-6">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-80px' }}
            variants={stagger}
            className="grid grid-cols-2 md:grid-cols-4 gap-10"
          >
            <StatCard value="98.2%" label="Fact-Check Accuracy" delay={0} />
            <StatCard value="< 3s" label="Average Analysis Time" delay={1} />
            <StatCard value="7" label="Data Sources Combined" delay={2} />
            <StatCard value="50k+" label="Claims Verified" delay={3} />
          </motion.div>
        </div>
      </section>

      {/* ── FEATURES ────────────────────────────────────────────────────── */}
      <section id="features" className="py-24 px-6 max-w-6xl mx-auto">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-60px' }}
          variants={stagger}
          className="space-y-16"
        >
          {/* Section Header */}
          <div className="text-center space-y-4">
            <motion.p
              variants={fadeUp}
              custom={0}
              className="text-xs uppercase tracking-widest text-emerald-400 font-medium"
            >
              Platform Features
            </motion.p>
            <motion.h2
              variants={fadeUp}
              custom={1}
              className="text-4xl md:text-5xl font-bold tracking-tight"
            >
              Everything you need to{' '}
              <span className="bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">
                verify truth
              </span>
            </motion.h2>
            <motion.p
              variants={fadeUp}
              custom={2}
              className="text-white/55 max-w-xl mx-auto"
            >
              TruthLens combines multiple AI models and live databases to give
              you a comprehensive trust score for any claim or image.
            </motion.p>
          </div>

          {/* Feature Grid */}
          <motion.div
            variants={stagger}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5"
          >
            <FeatureCard
              icon={Brain}
              title="Groq LLaMA-3.1 Analysis"
              description="Ultra-fast LLM reasoning on news claims using Groq's llama-3.1-70b model for contextual fact evaluation."
              delay={0}
            />
            <FeatureCard
              icon={Globe}
              title="Multi-Source Verification"
              description="Cross-references Google Fact Check, GDELT, NewsAPI, and MediaStack simultaneously for comprehensive coverage."
              delay={1}
            />
            <FeatureCard
              icon={ImageIcon}
              title="Deepfake Detection"
              description="Google Vision API + Hive Moderation AI detect AI-generated images, manipulations, and visual misinformation."
              delay={2}
            />
            <FeatureCard
              icon={BarChart3}
              title="Trust Score Engine"
              description="Weighted 0–100 trust score aggregated from all sources — LOW, MEDIUM, HIGH, or CRITICAL risk levels."
              delay={3}
            />
            <FeatureCard
              icon={Shield}
              title="Shareable Reports"
              description="Generate permanent, shareable trust report links for any analysis — perfect for journalists and researchers."
              delay={4}
            />
            <FeatureCard
              icon={Zap}
              title="Redis-Cached Speed"
              description="Redis TTL caching ensures repeated queries return instantly without burning API rate limits."
              delay={5}
            />
          </motion.div>
        </motion.div>
      </section>

      {/* ── HOW IT WORKS ────────────────────────────────────────────────── */}
      <section
        id="how-it-works"
        className="py-24 px-6 border-y border-white/10 bg-white/[0.015]"
      >
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-60px' }}
            variants={stagger}
            className="space-y-16"
          >
            <div className="text-center space-y-4">
              <motion.p
                variants={fadeUp}
                custom={0}
                className="text-xs uppercase tracking-widest text-teal-400 font-medium"
              >
                How It Works
              </motion.p>
              <motion.h2
                variants={fadeUp}
                custom={1}
                className="text-4xl md:text-5xl font-bold tracking-tight"
              >
                Verified in{' '}
                <span className="bg-gradient-to-r from-teal-400 to-emerald-400 bg-clip-text text-transparent">
                  3 simple steps
                </span>
              </motion.h2>
            </div>

            <motion.div
              variants={stagger}
              className="grid grid-cols-1 md:grid-cols-3 gap-12 relative"
            >
              {/* Connector line */}
              <div className="hidden md:block absolute top-7 left-[calc(16.67%+1rem)] right-[calc(16.67%+1rem)] h-px bg-gradient-to-r from-emerald-500/40 via-teal-500/40 to-green-500/40" />

              <StepCard
                number="1"
                title="Submit your claim"
                description="Paste a news URL, headline, or upload an image you want to verify."
                delay={0}
              />
              <StepCard
                number="2"
                title="AI multi-source scan"
                description="Our pipeline queries 7 APIs simultaneously and feeds results into Groq LLaMA for deep analysis."
                delay={1}
              />
              <StepCard
                number="3"
                title="Get your Trust Report"
                description="Receive a comprehensive trust score with evidence, source breakdown, and a shareable report link."
                delay={2}
              />
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* ── CTA SECTION ─────────────────────────────────────────────────── */}
      <section id="accuracy" className="py-28 px-6">
        <div className="max-w-3xl mx-auto">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-60px' }}
            variants={stagger}
            className="relative rounded-3xl border border-emerald-500/30 bg-gradient-to-br from-emerald-950/60 to-teal-950/40 backdrop-blur-sm p-12 text-center overflow-hidden"
          >
            {/* Glow */}
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-600/10 to-teal-600/10 rounded-3xl" />
            <div className="absolute -top-24 -right-24 w-64 h-64 bg-emerald-500/20 rounded-full blur-3xl" />
            <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-teal-500/20 rounded-full blur-3xl" />

            <div className="relative space-y-6">
              <motion.div
                variants={fadeUp}
                custom={0}
                className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/20 border border-emerald-400/30 text-emerald-300 text-xs font-medium"
              >
                <CheckCircle className="w-3 h-3" />
                Free to start — no credit card required
              </motion.div>

              <motion.h2
                variants={fadeUp}
                custom={1}
                className="text-4xl md:text-5xl font-bold tracking-tight"
              >
                Start verifying truth{' '}
                <span className="bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">
                  today
                </span>
              </motion.h2>

              <motion.p
                variants={fadeUp}
                custom={2}
                className="text-white/55 max-w-md mx-auto"
              >
                Join researchers, journalists, and citizens who trust TruthLens
                AI to separate fact from fiction.
              </motion.p>

              <motion.div
                variants={fadeUp}
                custom={3}
                className="flex flex-col sm:flex-row items-center justify-center gap-4"
              >
                <Link
                  href="/dashboard"
                  className="group flex items-center gap-2 px-8 py-3.5 rounded-full bg-gradient-to-r from-emerald-600 to-teal-600 text-white font-semibold text-sm hover:from-emerald-500 hover:to-teal-500 transition-all duration-200 shadow-2xl shadow-emerald-500/40 hover:-translate-y-0.5"
                >
                  Open Dashboard
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Link>
                <Link
                  href="/verify/news"
                  className="flex items-center gap-2 px-8 py-3.5 rounded-full border border-white/20 text-white/80 font-semibold text-sm hover:border-white/40 hover:text-white hover:bg-white/5 transition-all duration-200"
                >
                  <ExternalLink className="w-4 h-4" />
                  Try a quick verify
                </Link>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── FOOTER ──────────────────────────────────────────────────────── */}
      <footer className="border-t border-white/10 py-10 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-white/40">
          <div className="flex items-center gap-2">
            <div className="flex items-center justify-center w-6 h-6 rounded-md bg-gradient-to-br from-emerald-500 to-teal-500">
              <Shield className="w-3 h-3 text-white" />
            </div>
            <span>
              © 2025 <span className="text-white/60">TruthLens AI</span>. All rights reserved.
            </span>
          </div>
          <div className="flex items-center gap-6">
            <a href="#" className="hover:text-white/70 transition-colors">Privacy</a>
            <a href="#" className="hover:text-white/70 transition-colors">Terms</a>
            <a href="#" className="hover:text-white/70 transition-colors">Security</a>
            <a href="#" className="hover:text-white/70 transition-colors">API Docs</a>
          </div>
        </div>
      </footer>
    </main>
  );
}
