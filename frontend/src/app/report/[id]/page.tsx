'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Shield, ArrowLeft, Calendar, FileText, AlertTriangle, AlertCircle, CheckCircle, ExternalLink, BarChart2, Download, Mic, Globe, Tag, TrendingUp, X, Video, Zap } from 'lucide-react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { ShareButton } from '@/components/ui/share-button';
import {
  ReportHeaderSkeleton,
  ScoringGridSkeleton,
  AiReasoningSkeleton,
  NewsEvidenceSkeleton,
} from '@/components/ui/skeleton';

interface ReportDetails {
  ai_reasoning?: string;
  is_mock?: boolean;
  fact_checks?: any[];
  news_reports?: any[];
  hive_data?: { predictions?: any[] };
  vision_data?: { safeSearchAnnotation?: any; webDetection?: any };
  scoring_breakdown?: { deductions?: any[]; bonuses?: any[] };
  image_metadata?: any;
  url_context?: any;
  tone_analysis?: {
    overall_tone: string;
    tone_labels: string[];
    signals: any[];
    caps_ratio: number;
    exclamation_count: number;
    score_delta: number;
  };
  entities?: {
    organizations?: { abbr: string; full_name: string }[];
    quoted_sources?: { name: string; verified: boolean }[];
    years?: string[];
    dates?: string[];
    statistics?: string[];
    attribution_warnings?: string[];
  };
  confidence?: { low: number | null; high: number | null };
  sub_claims?: string[];
  cached_match?: boolean;
}

interface ReportData {
  id: string;
  type: string;
  query: string;
  status: string;
  trust_score: number | null;
  risk_level: string | null;
  created_at: string;
  details: ReportDetails | null;
}

export default function ReportDetailPage() {
  const params = useParams();
  const router = useRouter();
  const reportId = params.id as string;

  const [report, setReport] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const controller = new AbortController();
    const fetchReport = async () => {
      try {
        const data = await api.get<ReportData>(`/report/${reportId}`, controller.signal);
        setReport(data);
      } catch (err: any) {
        if (err.name === 'AbortError') return; // unmounted – ignore
        setError(err.message || 'Failed to load this verification report.');
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
    return () => controller.abort();
  }, [reportId]);

  // Dynamic colors based on risk level
  const getRiskStyles = (risk: string) => {
    switch (risk) {
      case 'LOW':
        return { text: 'text-emerald-400', border: 'border-emerald-500/20', bg: 'bg-emerald-500/10' };
      case 'MEDIUM':
        return { text: 'text-yellow-400', border: 'border-yellow-500/20', bg: 'bg-yellow-500/10' };
      case 'HIGH':
        return { text: 'text-orange-400', border: 'border-orange-500/20', bg: 'bg-orange-500/10' };
      default:
        return { text: 'text-red-400', border: 'border-red-500/20', bg: 'bg-red-500/10' };
    }
  };

  // Lightweight Markdown renderer for LLaMA output
  const formatReasoning = (text: string = '') => {
    // Bold inline: **text** → <strong>text</strong>
    const renderInline = (s: string) => {
      const parts = s.split(/(\*\*[^*]+\*\*)/g);
      return parts.map((part, i) =>
        part.startsWith('**') && part.endsWith('**')
          ? <strong key={i} className="text-white font-semibold">{part.slice(2, -2)}</strong>
          : <span key={i}>{part}</span>
      );
    };

    return text.split('\n').map((line, idx) => {
      const trimmed = line.trim();
      // Check #### before ### to avoid false prefix match
      if (trimmed.startsWith('####')) {
        return <h4 key={idx} className="text-base font-bold text-white mt-4 mb-1">{trimmed.replace(/^#{4}\s*/, '')}</h4>;
      }
      if (trimmed.startsWith('###')) {
        return <h3 key={idx} className="text-lg font-bold text-white mt-6 mb-2">{trimmed.replace(/^#{3}\s*/, '')}</h3>;
      }
      if (trimmed.startsWith('## ')) {
        return <h2 key={idx} className="text-xl font-bold text-white mt-6 mb-2">{trimmed.replace(/^#{2}\s*/, '')}</h2>;
      }
      if (trimmed.startsWith('- ') || (trimmed.startsWith('* ') && !trimmed.startsWith('**'))) {
        return (
          <li key={idx} className="text-sm text-white/75 leading-relaxed ml-5 list-disc mt-1.5">
            {renderInline(trimmed.substring(2))}
          </li>
        );
      }
      if (trimmed.match(/^\d+\.\s/)) {
        return (
          <li key={idx} className="text-sm text-white/75 leading-relaxed ml-5 list-decimal mt-1.5">
            {renderInline(trimmed.replace(/^\d+\.\s/, ''))}
          </li>
        );
      }
      if (trimmed === '') return <div key={idx} className="h-2" />;
      return <p key={idx} className="text-sm text-white/70 leading-relaxed mt-2">{renderInline(trimmed)}</p>;
    });
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-[#030712] text-white">
        {/* Nav skeleton */}
        <nav className="border-b border-white/10 bg-white/[0.02] px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-white/10 animate-pulse" />
            <div className="w-28 h-5 skeleton rounded" />
          </div>
          <div className="w-20 h-7 skeleton rounded-full" />
        </nav>
        <div className="max-w-5xl mx-auto px-6 py-10 space-y-8">
          <ReportHeaderSkeleton />
          <ScoringGridSkeleton />
          <AiReasoningSkeleton />
          <NewsEvidenceSkeleton />
        </div>
      </main>
    );
  }

  if (error || !report) {
    return (
      <div className="min-h-screen bg-[#030712] text-white flex flex-col items-center justify-center gap-4 px-4">
        <AlertTriangle className="w-12 h-12 text-red-400" />
        <p className="text-sm text-white/50">{error || 'Verification report not found.'}</p>
        <Link href="/" className="px-5 py-2.5 rounded-full border border-white/10 text-xs font-semibold hover:bg-white/5">
          Go Home
        </Link>
      </div>
    );
  }

  const riskStyles = getRiskStyles(report.risk_level || 'CRITICAL');
  const details = report.details || {};

  return (
    <main className="min-h-screen bg-[#030712] text-white">
      {/* Top Banner if mock */}
      {details.is_mock && (
        <div className="w-full bg-amber-500/10 border-b border-amber-500/25 py-2 px-6 flex items-center justify-center gap-2 text-xs text-amber-300">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span><strong>Prototype Mode:</strong> Live API credentials are not configured. Running on sandbox mock simulations.</span>
        </div>
      )}

      {/* Navigation */}
      <nav className="border-b border-white/10 bg-white/[0.02] px-6 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500">
            <Shield className="w-4 h-4 text-white" />
          </div>
          <span className="text-lg font-bold tracking-tight text-white">TruthLens <span className="text-xs text-white/40">Report</span></span>
        </Link>
        <div className="flex items-center gap-2">
          <ShareButton reportId={reportId} />
          <button
            onClick={() => window.print()}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-full border border-white/10 text-xs text-white/70 hover:text-white hover:border-emerald-500/40 transition-all cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span>PDF</span>
          </button>
          <button
            onClick={() => {
              if (api.isAuthenticated()) router.push('/dashboard');
              else router.push('/');
            }}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-full border border-white/10 text-xs text-white/70 hover:text-white cursor-pointer"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Dashboard</span>
          </button>
        </div>
      </nav>

      {/* Content wrapper */}
      <div className="max-w-5xl mx-auto px-6 py-10 space-y-8">
        
        {/* Fast-Tracked Deepfake Banner */}
        {details.cached_match && (
          <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4 flex items-center gap-3">
            <div className="bg-emerald-500/20 p-2 rounded-lg">
              <Zap className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <h3 className="text-emerald-400 font-bold text-sm">Fast-Tracked: Previously Verified Deepfake</h3>
              <p className="text-emerald-400/80 text-xs mt-0.5">This exact image has been analyzed previously. Serving cached results from our perceptual hashing database.</p>
            </div>
          </div>
        )}

        {/* Claim Query Box */}
        <div className="glass-card p-6 border border-white/10 bg-white/5 rounded-2xl">
          <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-white/40 mb-3">
            <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full font-medium ${
              report.type === 'news' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-teal-500/10 text-teal-400'
            }`}>
              {report.type === 'news' ? 'News Claim Verification' : 'Image Verification'}
            </span>
            <span className="flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5" />
              {new Date(report.created_at).toLocaleString()}
            </span>
          </div>
          <h2 className="text-lg md:text-xl font-bold leading-relaxed text-white">
            &ldquo;{report.query}&rdquo;
          </h2>

          {/* AI Decomposed Sub-claims */}
          {details.sub_claims && details.sub_claims.length > 0 && (
            <div className="mt-4 pt-4 border-t border-white/10">
              <p className="text-xs text-white/40 font-semibold mb-2 flex items-center gap-1">
                <Zap className="w-3 h-3 text-purple-400" /> AI Decomposed Sub-claims
              </p>
              <div className="flex flex-col gap-2">
                {details.sub_claims.map((claim, idx) => (
                  <div key={idx} className="flex items-start gap-2 bg-white/5 border border-white/5 rounded-lg p-2.5">
                    <span className="text-[10px] font-bold text-white/30 bg-white/10 px-1.5 py-0.5 rounded">#{idx + 1}</span>
                    <span className="text-sm text-white/80">{claim}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Scraped URL article context */}
          {details.url_context?.scraped && (
            <div className="mt-4 p-4 rounded-xl bg-white/[0.03] border border-white/10 space-y-2">
              <div className="flex items-center gap-2 text-xs text-emerald-400 font-semibold">
                {details.url_context.platform_type === 'twitter' ? (
                  <X className="w-3.5 h-3.5 text-blue-400" />
                ) : details.url_context.platform_type === 'youtube' ? (
                  <Video className="w-3.5 h-3.5 text-red-500" />
                ) : (
                  <Globe className="w-3.5 h-3.5" />
                )}
                <span className={details.url_context.platform_type === 'twitter' ? 'text-blue-400' : details.url_context.platform_type === 'youtube' ? 'text-red-500' : ''}>
                  {details.url_context.platform_type === 'twitter' ? 'X (Twitter) Post' : details.url_context.platform_type === 'youtube' ? 'YouTube Video' : 'Article Scraped from URL'}
                </span>
                <span className={`ml-auto px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                  details.url_context.domain_credibility?.rating === 'HIGH'
                    ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                    : details.url_context.domain_credibility?.rating === 'LOW'
                    ? 'bg-red-500/10 border-red-500/20 text-red-400'
                    : 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400'
                }`}>
                  {details.url_context.domain_credibility?.label}
                </span>
              </div>
              {details.url_context.title && (
                <p className="text-sm font-semibold text-white/90">{details.url_context.title}</p>
              )}
              <div className="flex flex-wrap gap-3 text-xs text-white/40">
                {details.url_context.author && <span>By {details.url_context.author}</span>}
                {details.url_context.published_at && <span>{new Date(details.url_context.published_at).toLocaleDateString()}</span>}
                <a href={details.url_context.url} target="_blank" rel="noopener noreferrer"
                  className="text-emerald-400 hover:underline inline-flex items-center gap-0.5">
                  {details.url_context.domain} <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          )}
        </div>

        {/* Scoring & Risk Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Trust Score Radial Gauge */}
          <div className="glass-card p-6 border border-white/10 bg-white/5 rounded-2xl flex flex-col items-center justify-center text-center">
            <h3 className="text-xs uppercase tracking-wider text-white/40 font-semibold mb-4">Calculated Trust Score</h3>
            <div className="relative w-36 h-36 flex items-center justify-center">
              <svg className="w-full h-full transform -rotate-90">
                <circle cx="72" cy="72" r="62" stroke="rgba(255,255,255,0.05)" strokeWidth="8" fill="transparent" />
                <circle
                  cx="72"
                  cy="72"
                  r="62"
                  stroke={report.trust_score && report.trust_score >= 75 ? '#10b981' : report.trust_score && report.trust_score >= 50 ? '#eab308' : report.trust_score && report.trust_score >= 25 ? '#f97316' : '#ef4444'}
                  strokeWidth="8"
                  fill="transparent"
                  strokeDasharray={2 * Math.PI * 62}
                  strokeDashoffset={2 * Math.PI * 62 * (1 - (report.trust_score || 0) / 100)}
                  className="transition-all duration-1000 ease-out"
                />
              </svg>
              <div className="absolute flex flex-col items-center">
                <span className="text-3xl font-extrabold">{report.trust_score}%</span>
                <span className="text-[10px] text-white/40 uppercase tracking-widest mt-0.5">Credibility</span>
              </div>
            </div>
            {/* Confidence Interval Bar */}
            {details.confidence?.low != null && details.confidence?.high != null && (
              <div className="mt-4 w-full space-y-1">
                <div className="flex justify-between text-[10px] text-white/30">
                  <span>{details.confidence.low}%</span>
                  <span className="text-white/50 font-semibold">±{Math.round(((details.confidence.high ?? 0) - (details.confidence.low ?? 0)) / 2)}pt range</span>
                  <span>{details.confidence.high}%</span>
                </div>
                <div className="relative w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                  <div
                    className="absolute h-full rounded-full bg-white/20"
                    style={{
                      left: `${details.confidence.low}%`,
                      width: `${(details.confidence.high ?? 0) - (details.confidence.low ?? 0)}%`,
                    }}
                  />
                  <div
                    className="absolute w-1 h-full bg-emerald-400 rounded-full"
                    style={{ left: `${report.trust_score ?? 0}%`, transform: 'translateX(-50%)' }}
                  />
                </div>
                <p className="text-[10px] text-white/25 text-center">Confidence Interval</p>
              </div>
            )}
          </div>

          {/* Risk Level Card */}
          <div className="glass-card p-6 border border-white/10 bg-white/5 rounded-2xl flex flex-col justify-between">
            <div>
              <h3 className="text-xs uppercase tracking-wider text-white/40 font-semibold">Risk Level Assessment</h3>
              <div className="mt-4">
                <span className={`inline-flex items-center px-3.5 py-1 rounded-md text-sm font-extrabold uppercase tracking-widest ${riskStyles.text} ${riskStyles.bg} border ${riskStyles.border}`}>
                  {report.risk_level} RISK
                </span>
              </div>
              <p className="text-xs text-white/50 mt-4 leading-relaxed">
                {report.risk_level === 'LOW' && 'This content matches established truth metrics. There is no indicating footprint of alteration or rumors.'}
                {report.risk_level === 'MEDIUM' && 'Some inconsistencies or missing details were detected. Double check supporting materials.'}
                {report.risk_level === 'HIGH' && 'Significant anomalies or red flags were found. Treat this statement with high skepticism.'}
                {report.risk_level === 'CRITICAL' && 'Debunked claims or manipulated elements detected. Highly likely to be misinformation.'}
              </p>
            </div>
          </div>

          {/* Core Deductions / Bonuses list */}
          <div className="glass-card p-6 border border-white/10 bg-white/5 rounded-2xl flex flex-col justify-between">
            <div>
              <h3 className="text-xs uppercase tracking-wider text-white/40 font-semibold mb-3">Verification Details</h3>
              <div className="space-y-3 max-h-[200px] overflow-y-auto pr-1">
                {details.scoring_breakdown?.deductions?.map((ded: any, i: number) => {
                  const text = typeof ded === 'string' ? ded : ded.text;
                  const url = typeof ded === 'string' ? '' : ded.url;
                  const source = typeof ded === 'string' ? '' : ded.source;
                  return (
                    <div key={i} className="space-y-1">
                      <div className="text-xs text-red-400 flex items-start gap-1.5">
                        <AlertCircle className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" />
                        <span>{text}</span>
                      </div>
                      {url && (
                        <a
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="ml-5 inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-red-500/10 border border-red-500/20 text-red-400/80 hover:text-red-300 hover:bg-red-500/20 transition-all"
                        >
                          <ExternalLink className="w-2.5 h-2.5" />
                          {source || 'Source'}
                        </a>
                      )}
                    </div>
                  );
                })}
                {details.scoring_breakdown?.bonuses?.map((bon: any, i: number) => {
                  const text = typeof bon === 'string' ? bon : bon.text;
                  const url = typeof bon === 'string' ? '' : bon.url;
                  const source = typeof bon === 'string' ? '' : bon.source;
                  return (
                    <div key={i} className="space-y-1">
                      <div className="text-xs text-emerald-400 flex items-start gap-1.5">
                        <CheckCircle className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" />
                        <span>{text}</span>
                      </div>
                      {url && (
                        <a
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="ml-5 inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400/80 hover:text-emerald-300 hover:bg-emerald-500/20 transition-all"
                        >
                          <ExternalLink className="w-2.5 h-2.5" />
                          {source || 'Source'}
                        </a>
                      )}
                    </div>
                  );
                })}
                {!details.scoring_breakdown?.deductions?.length && !details.scoring_breakdown?.bonuses?.length && (
                  <p className="text-xs text-white/35 italic">No notable score deductions or bonuses applied.</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* AI Reasoning Section */}
        <div className="glass-card p-8 border border-white/10 bg-white/5 rounded-2xl">
          <div className="flex items-center gap-2 border-b border-white/10 pb-4 mb-4">
            <FileText className="w-5 h-5 text-emerald-400" />
            <h3 className="font-bold text-lg">AI Contextual Reasoning Analysis</h3>
          </div>
          <div className="prose prose-invert max-w-none">
            {formatReasoning(details.ai_reasoning)}
          </div>
        </div>

        {/* Tone Analysis Widget — News only */}
        {report.type === 'news' && details.tone_analysis && (
          <div className="glass-card p-6 border border-white/10 bg-white/5 rounded-2xl">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Mic className="w-4 h-4 text-purple-400" />
                <h3 className="font-bold text-base text-white/80">Emotional Tone & Rhetoric Analysis</h3>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-bold border ${
                details.tone_analysis.overall_tone === 'Neutral'
                  ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                  : details.tone_analysis.overall_tone === 'Fear-Inducing' || details.tone_analysis.overall_tone === 'Outrage Bait'
                  ? 'bg-orange-500/10 border-orange-500/20 text-orange-400'
                  : 'bg-red-500/10 border-red-500/20 text-red-400'
              }`}>
                {details.tone_analysis.overall_tone}
              </span>
            </div>
            {details.tone_analysis.signals.length > 0 ? (
              <div className="space-y-3">
                {details.tone_analysis.signals.map((sig: any, i: number) => (
                  <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-white/[0.02] border border-white/5">
                    <span className={`text-lg ${
                      sig.type === 'fear' ? '😨' : sig.type === 'outrage' ? '😡' :
                      sig.type === 'propaganda' ? '📢' : sig.type === 'caps' ? '🔊' : '❗'
                    }`}>{sig.type === 'fear' ? '😨' : sig.type === 'outrage' ? '😡' : sig.type === 'propaganda' ? '📢' : sig.type === 'caps' ? '🔊' : '❗'}</span>
                    <div>
                      <p className="text-xs font-semibold text-white/80">{sig.label}</p>
                      <p className="text-xs text-white/45 mt-0.5">{sig.detail}</p>
                    </div>
                    <span className="ml-auto text-xs font-bold text-red-400">{sig.score_delta}pts</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-white/40 italic">No emotional manipulation signals detected. Language appears measured and neutral.</p>
            )}
            <div className="flex gap-4 mt-4 pt-4 border-t border-white/5 text-xs text-white/40">
              <span>CAPS ratio: <strong className="text-white/60">{details.tone_analysis.caps_ratio}%</strong></span>
              <span>Exclamations: <strong className="text-white/60">{details.tone_analysis.exclamation_count}</strong></span>
            </div>
          </div>
        )}

        {/* Entity Tags — News only */}
        {report.type === 'news' && details.entities && (
          (() => {
            const ent = details.entities;
            const hasEntities = (ent.organizations?.length || 0) + (ent.statistics?.length || 0) + (ent.years?.length || 0) + (ent.quoted_sources?.length || 0) > 0;
            if (!hasEntities) return null;
            return (
              <div className="glass-card p-6 border border-white/10 bg-white/5 rounded-2xl">
                <div className="flex items-center gap-2 mb-4">
                  <Tag className="w-4 h-4 text-cyan-400" />
                  <h3 className="font-bold text-base text-white/80">Named Entity Extraction</h3>
                </div>
                <div className="space-y-4">
                  {ent.organizations && ent.organizations.length > 0 && (
                    <div>
                      <p className="text-xs uppercase tracking-wider text-white/30 font-semibold mb-2">Organizations Cited</p>
                      <div className="flex flex-wrap gap-2">
                        {ent.organizations.map((org: any, i: number) => (
                          <span key={i} className="px-2.5 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-300 text-xs font-semibold" title={org.full_name}>
                            {org.abbr}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {ent.statistics && ent.statistics.length > 0 && (
                    <div>
                      <p className="text-xs uppercase tracking-wider text-white/30 font-semibold mb-2">Statistics Detected</p>
                      <div className="flex flex-wrap gap-2">
                        {ent.statistics.slice(0, 6).map((stat: string, i: number) => (
                          <span key={i} className="px-2.5 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300 text-xs font-semibold">
                            {stat}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {ent.years && ent.years.length > 0 && (
                    <div>
                      <p className="text-xs uppercase tracking-wider text-white/30 font-semibold mb-2">Years Referenced</p>
                      <div className="flex flex-wrap gap-2">
                        {ent.years.map((y: string, i: number) => (
                          <span key={i} className="px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-semibold">{y}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {ent.attribution_warnings && ent.attribution_warnings.length > 0 && (
                    <div className="p-3 rounded-xl bg-amber-500/5 border border-amber-500/20">
                      <p className="text-xs text-amber-300/80">
                        ⚠️ {ent.attribution_warnings[0]}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            );
          })()
        )}

        {/* News Type Evidence: Fact Checks & Media Coverage */}
        {report.type === 'news' && (
          <div className="space-y-8">
            {/* Fact Check Matches */}
            {details.fact_checks && details.fact_checks.length > 0 && (
              <div className="glass-card p-6 border border-white/10 bg-white/5 rounded-2xl">
                <h3 className="font-bold text-base mb-4 flex items-center gap-2 text-white/80">
                  <Shield className="w-4 h-4 text-emerald-400" />
                  Fact-Checking Archive Hits
                </h3>
                <div className="space-y-4">
                  {details.fact_checks.map((fc, i) => (
                    <div key={i} className="p-4 rounded-xl bg-white/[0.02] border border-white/5 space-y-2">
                      <div className="flex items-start justify-between gap-3">
                        <p className="text-sm font-semibold">{fc.claimText}</p>
                        <span className="text-xs font-medium px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/25">
                          {fc.claimReview?.[0]?.textualRating || 'False'}
                        </span>
                      </div>
                      <div className="flex justify-between items-center text-xs text-white/40 pt-1">
                        <span>Verified by: <strong>{fc.claimReview?.[0]?.publisher?.name || 'Snopes'}</strong></span>
                        {fc.claimReview?.[0]?.url && (
                          <a
                            href={fc.claimReview[0].url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-emerald-400 hover:underline inline-flex items-center gap-0.5"
                          >
                            Read Full Debunk <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Media reports */}
            {details.news_reports && details.news_reports.length > 0 && (
              <div className="glass-card p-6 border border-white/10 bg-white/5 rounded-2xl">
                <h3 className="font-bold text-base mb-4 flex items-center gap-2 text-white/80">
                  <BarChart2 className="w-4 h-4 text-emerald-400" />
                  Widespread Media Coverage Reports
                </h3>
                <div className="space-y-4">
                  {details.news_reports.map((art, i) => (
                    <div key={i} className="p-4 rounded-xl bg-white/[0.01] hover:bg-white/[0.02] border border-white/5 space-y-2 transition-all">
                      <div className="flex justify-between items-start gap-4">
                        <h4 className="text-sm font-semibold text-white/95">{art.title}</h4>
                        <span className="text-[10px] uppercase font-bold text-white/35 tracking-wider bg-white/5 px-2 py-0.5 rounded">
                          {art.source}
                        </span>
                      </div>
                      <p className="text-xs text-white/50 leading-relaxed">{art.description}</p>
                      {art.url && (
                        <div className="pt-1">
                          <a
                            href={art.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-emerald-400 hover:text-emerald-300 text-xs font-semibold inline-flex items-center gap-0.5"
                          >
                            Visit Article Source <ExternalLink className="w-3 h-3" />
                          </a>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Image Type Evidence: Deepfake probability & Visual searches */}
        {report.type === 'image' && (
          <div className="space-y-8">
            {/* Deepfake Predictor */}
            {details.hive_data?.predictions && (
              <div className="glass-card p-6 border border-white/10 bg-white/5 rounded-2xl">
                <h3 className="font-bold text-base mb-4 flex items-center gap-2 text-white/80">
                  <Shield className="w-4 h-4 text-emerald-400" />
                  Hive Moderation Deepfake / AI Scan
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {details.hive_data.predictions.map((pred: any, i: number) => (
                    <div key={i} className="p-4 rounded-xl bg-white/[0.02] border border-white/5">
                      <span className="text-xs text-white/40 uppercase font-semibold tracking-wider">{pred.class.replace('_', ' ')}</span>
                      <div className="text-xl font-bold mt-1 text-white">{(pred.score * 100).toFixed(1)}%</div>
                      {/* simple bar */}
                      <div className="w-full bg-white/5 h-1.5 rounded-full mt-2 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${pred.class === 'original' ? 'bg-emerald-400' : 'bg-red-400'}`}
                          style={{ width: `${pred.score * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* EXIF Metadata Analyzer */}
            {details.image_metadata && (
              <div className="glass-card p-6 border border-white/10 bg-white/5 rounded-2xl">
                <h3 className="font-bold text-base mb-4 flex items-center gap-2 text-white/80">
                  <FileText className="w-4 h-4 text-emerald-400" />
                  Metadata & EXIF Forensic Analysis
                </h3>
                
                {!details.image_metadata.has_exif ? (
                  <div className="p-4 rounded-xl bg-red-500/5 border border-red-500/10 text-xs text-red-400/90 leading-relaxed">
                    <strong>No EXIF metadata detected.</strong> This indicates the image has been stripped of metadata, is a screenshot, or was generated directly by an AI model.
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
                    {/* Capture Time & Specs */}
                    <div className="space-y-3">
                      <h4 className="text-xs uppercase font-bold text-white/40 tracking-wider">File & Capture Specs</h4>
                      <div className="space-y-2 text-xs">
                        <div className="flex justify-between border-b border-white/5 pb-1">
                          <span className="text-white/50">Format</span>
                          <span className="font-semibold text-white/80">{details.image_metadata.format?.format || 'Unknown'} ({details.image_metadata.format?.mode || 'RGB'})</span>
                        </div>
                        <div className="flex justify-between border-b border-white/5 pb-1">
                          <span className="text-white/50">Dimensions</span>
                          <span className="font-semibold text-white/80">{details.image_metadata.dimensions?.width} × {details.image_metadata.dimensions?.height}</span>
                        </div>
                        <div className="flex justify-between border-b border-white/5 pb-1">
                          <span className="text-white/50">Resolution</span>
                          <span className="font-semibold text-white/80">{details.image_metadata.dimensions?.megapixels} MP</span>
                        </div>
                        <div className="flex justify-between border-b border-white/5 pb-1">
                          <span className="text-white/50">Capture Date</span>
                          <span className="font-semibold text-white/80 truncate max-w-[120px]" title={details.image_metadata.capture_time?.formatted}>{details.image_metadata.capture_time?.formatted || 'Not recorded'}</span>
                        </div>
                      </div>
                    </div>

                    {/* Camera Information */}
                    <div className="space-y-3">
                      <h4 className="text-xs uppercase font-bold text-white/40 tracking-wider">Camera & Hardware</h4>
                      <div className="space-y-2 text-xs">
                        <div className="flex justify-between border-b border-white/5 pb-1">
                          <span className="text-white/50">Camera Make</span>
                          <span className="font-semibold text-white/80 truncate max-w-[120px]" title={details.image_metadata.camera?.Make}>{details.image_metadata.camera?.Make || 'Unknown'}</span>
                        </div>
                        <div className="flex justify-between border-b border-white/5 pb-1">
                          <span className="text-white/50">Model</span>
                          <span className="font-semibold text-white/80 truncate max-w-[120px]" title={details.image_metadata.camera?.Model}>{details.image_metadata.camera?.Model || 'Unknown'}</span>
                        </div>
                        <div className="flex justify-between border-b border-white/5 pb-1">
                          <span className="text-white/50">Lens Model</span>
                          <span className="font-semibold text-white/80 truncate max-w-[120px]" title={details.image_metadata.camera?.LensModel}>{details.image_metadata.camera?.LensModel || 'Unknown'}</span>
                        </div>
                        <div className="flex justify-between border-b border-white/5 pb-1">
                          <span className="text-white/50">Software</span>
                          <span className="font-semibold text-white/80 truncate max-w-[120px]" title={details.image_metadata.camera?.Software}>{details.image_metadata.camera?.Software || 'Camera Firmware'}</span>
                        </div>
                      </div>
                    </div>

                    {/* Exposure Settings */}
                    <div className="space-y-3">
                      <h4 className="text-xs uppercase font-bold text-white/40 tracking-wider">Exposure Settings</h4>
                      <div className="space-y-2 text-xs">
                        <div className="flex justify-between border-b border-white/5 pb-1">
                          <span className="text-white/50">Aperture</span>
                          <span className="font-semibold text-white/80">{details.image_metadata.settings?.FNumber ? `f/${details.image_metadata.settings.FNumber}` : 'N/A'}</span>
                        </div>
                        <div className="flex justify-between border-b border-white/5 pb-1">
                          <span className="text-white/50">Exposure Time</span>
                          <span className="font-semibold text-white/80">{details.image_metadata.settings?.ExposureTime ? `${details.image_metadata.settings.ExposureTime}s` : 'N/A'}</span>
                        </div>
                        <div className="flex justify-between border-b border-white/5 pb-1">
                          <span className="text-white/50">ISO Speed</span>
                          <span className="font-semibold text-white/80">{details.image_metadata.settings?.ISOSpeedRatings || 'N/A'}</span>
                        </div>
                        <div className="flex justify-between border-b border-white/5 pb-1">
                          <span className="text-white/50">Focal Length</span>
                          <span className="font-semibold text-white/80">{details.image_metadata.settings?.FocalLength ? `${details.image_metadata.settings.FocalLength}mm` : 'N/A'}</span>
                        </div>
                      </div>
                    </div>

                    {/* Geolocation */}
                    <div className="space-y-3">
                      <h4 className="text-xs uppercase font-bold text-white/40 tracking-wider">Geolocation Info</h4>
                      <div className="space-y-2 text-xs">
                        {details.image_metadata.gps?.latitude ? (
                          <>
                            <div className="flex justify-between border-b border-white/5 pb-1">
                              <span className="text-white/50">Latitude</span>
                              <span className="font-semibold text-white/80">{details.image_metadata.gps.latitude}</span>
                            </div>
                            <div className="flex justify-between border-b border-white/5 pb-1">
                              <span className="text-white/50">Longitude</span>
                              <span className="font-semibold text-white/80">{details.image_metadata.gps.longitude}</span>
                            </div>
                            {details.image_metadata.gps.altitude_m && (
                              <div className="flex justify-between border-b border-white/5 pb-1">
                                <span className="text-white/50">Altitude</span>
                                <span className="font-semibold text-white/80">{details.image_metadata.gps.altitude_m}m</span>
                              </div>
                            )}
                            <div className="pt-1">
                              <a
                                href={details.image_metadata.gps.maps_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-emerald-400 hover:text-emerald-300 font-semibold inline-flex items-center gap-0.5"
                              >
                                View on Google Maps <ExternalLink className="w-3 h-3" />
                              </a>
                            </div>
                          </>
                        ) : (
                          <div className="text-white/35 italic">No GPS coordinates embedded in file metadata.</div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Google Vision SafeSearch & Visual Web Match index */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Safe Search */}
              {details.vision_data?.safeSearchAnnotation && (
                <div className="glass-card p-6 border border-white/10 bg-white/5 rounded-2xl">
                  <h3 className="font-bold text-base mb-4 text-white/80">SafeSearch Content Flags</h3>
                  <div className="space-y-2">
                    {Object.entries(details.vision_data.safeSearchAnnotation).map(([key, val]: any) => (
                      <div key={key} className="flex justify-between items-center text-xs py-1.5 border-b border-white/5 last:border-0">
                        <span className="text-white/60 capitalize">{key}</span>
                        <span className={`font-semibold ${
                          val === 'VERY_UNLIKELY' || val === 'UNLIKELY' ? 'text-emerald-400' : 'text-red-400'
                        }`}>{val.replace('_', ' ')}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Visually Similar matching pages */}
              {details.vision_data?.webDetection?.pagesWithMatchingImages && (
                <div className="glass-card p-6 border border-white/10 bg-white/5 rounded-2xl">
                  <h3 className="font-bold text-base mb-4 text-white/80">Online Image Matches</h3>
                  <div className="space-y-3.5 max-h-[220px] overflow-y-auto pr-1">
                    {details.vision_data.webDetection.pagesWithMatchingImages.map((page: any, i: number) => (
                      <div key={i} className="text-xs space-y-1">
                        <h4 className="font-semibold text-white/90 truncate">{page.pageTitle || 'Visual Match Source'}</h4>
                        <a
                          href={page.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-emerald-400 hover:underline inline-flex items-center gap-0.5 truncate max-w-full"
                        >
                          Visit Page URL <ExternalLink className="w-3 h-3 flex-shrink-0" />
                        </a>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

      </div>
    </main>
  );
}
