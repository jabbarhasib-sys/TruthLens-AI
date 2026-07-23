/**
 * Skeleton shimmer primitives.
 * Use these to match the exact shape of analysis report cards,
 * reducing perceived latency during data fetching.
 */
import React from 'react';
import { cn } from '@/lib/utils';

// ── Base Skeleton ────────────────────────────────────────────────────────────
interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {}

export function Skeleton({ className, ...props }: SkeletonProps) {
  return (
    <div
      aria-hidden="true"
      className={cn('skeleton', className)}
      {...props}
    />
  );
}

// ── Report Header Skeleton ───────────────────────────────────────────────────
export function ReportHeaderSkeleton() {
  return (
    <div className="glass-card p-6 border border-white/10 rounded-2xl space-y-3">
      {/* Badge + date row */}
      <div className="flex items-center justify-between">
        <Skeleton className="h-5 w-32 rounded-full" />
        <Skeleton className="h-4 w-36" />
      </div>
      {/* Title */}
      <Skeleton className="h-6 w-full" />
      <Skeleton className="h-6 w-4/5" />
    </div>
  );
}

// ── Scoring Grid Skeleton ────────────────────────────────────────────────────
export function ScoringGridSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Radial gauge */}
      <div className="glass-card p-6 border border-white/10 rounded-2xl flex flex-col items-center gap-4">
        <Skeleton className="h-3 w-32 rounded-full" />
        <Skeleton className="w-36 h-36 rounded-full" />
      </div>

      {/* Risk level */}
      <div className="glass-card p-6 border border-white/10 rounded-2xl space-y-4">
        <Skeleton className="h-3 w-28" />
        <Skeleton className="h-7 w-24 rounded-md" />
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-5/6" />
      </div>

      {/* Verification details */}
      <div className="glass-card p-6 border border-white/10 rounded-2xl space-y-3">
        <Skeleton className="h-3 w-36" />
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-4/5" />
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-3/4" />
      </div>
    </div>
  );
}

// ── AI Reasoning Skeleton ────────────────────────────────────────────────────
export function AiReasoningSkeleton() {
  return (
    <div className="glass-card p-8 border border-white/10 rounded-2xl space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2 border-b border-white/10 pb-4 mb-2">
        <Skeleton className="w-5 h-5 rounded" />
        <Skeleton className="h-5 w-56" />
      </div>
      {/* Body paragraphs */}
      {[100, 90, 100, 75, 100, 60, 100, 85].map((w, i) => (
        <Skeleton key={i} className={`h-3 w-[${w}%]`} />
      ))}
    </div>
  );
}

// ── News Evidence Skeleton ───────────────────────────────────────────────────
export function NewsEvidenceSkeleton() {
  return (
    <div className="space-y-8">
      {/* Fact checks */}
      <div className="glass-card p-6 border border-white/10 rounded-2xl space-y-4">
        <div className="flex items-center gap-2">
          <Skeleton className="w-4 h-4 rounded" />
          <Skeleton className="h-4 w-44" />
        </div>
        {[0, 1].map((i) => (
          <div key={i} className="p-4 rounded-xl bg-white/[0.02] border border-white/5 space-y-2">
            <div className="flex justify-between gap-3">
              <Skeleton className="h-4 w-4/5" />
              <Skeleton className="h-5 w-14 rounded-full" />
            </div>
            <Skeleton className="h-3 w-48" />
          </div>
        ))}
      </div>
      {/* Media coverage */}
      <div className="glass-card p-6 border border-white/10 rounded-2xl space-y-4">
        <div className="flex items-center gap-2">
          <Skeleton className="w-4 h-4 rounded" />
          <Skeleton className="h-4 w-52" />
        </div>
        {[0, 1, 2].map((i) => (
          <div key={i} className="p-4 rounded-xl bg-white/[0.01] border border-white/5 space-y-2">
            <div className="flex justify-between gap-3">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-16 rounded" />
            </div>
            <Skeleton className="h-3 w-full" />
            <Skeleton className="h-3 w-1/3" />
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Dashboard Stats Skeleton ─────────────────────────────────────────────────
export function DashboardStatsSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
      {[0, 1, 2, 3].map((i) => (
        <div key={i} className="glass-card p-6 border border-white/10 rounded-2xl space-y-3">
          <Skeleton className="h-3 w-28" />
          <Skeleton className="h-8 w-16" />
        </div>
      ))}
    </div>
  );
}

// ── Dashboard History Table Skeleton ─────────────────────────────────────────
export function DashboardHistorySkeleton() {
  return (
    <div className="divide-y divide-white/5">
      {[0, 1, 2, 3, 4].map((i) => (
        <div key={i} className="px-6 py-4 flex items-center gap-4">
          <Skeleton className="h-5 w-20 rounded-full" />
          <Skeleton className="h-4 flex-1 max-w-xs" />
          <Skeleton className="h-4 w-20 ml-auto hidden md:block" />
          <Skeleton className="h-5 w-14 rounded-full hidden md:block" />
          <Skeleton className="h-5 w-14 rounded-full hidden md:block" />
          <Skeleton className="h-4 w-16 hidden md:block" />
        </div>
      ))}
    </div>
  );
}
