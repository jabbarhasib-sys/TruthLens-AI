'use client';

import React, { useState } from 'react';
import { Copy, Check, Share2 } from 'lucide-react';

interface ShareButtonProps {
  reportId: string;
  className?: string;
}

/**
 * ShareButton — copies the full shareable URL for a verification report to
 * the clipboard and shows a brief confirmation tick.
 *
 * The UUID is embedded in the URL path so judges can bookmark or share the
 * exact page without any login requirement.
 */
export function ShareButton({ reportId, className = '' }: ShareButtonProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      const url =
        typeof window !== 'undefined'
          ? `${window.location.origin}/report/${reportId}`
          : `/report/${reportId}`;

      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      // Fallback: manual selection (Safari < 13.1, Firefox non-secure)
      const textArea = document.createElement('textarea');
      textArea.value = `/report/${reportId}`;
      textArea.style.position = 'fixed';
      textArea.style.opacity = '0';
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  return (
    <button
      id={`share-report-${reportId}`}
      onClick={handleCopy}
      aria-label="Copy shareable report link"
      title={copied ? 'Link copied!' : 'Copy shareable link'}
      className={[
        'flex items-center gap-1.5',
        'px-3.5 py-1.5 rounded-full',
        'border text-xs font-semibold',
        'transition-all duration-200',
        copied
          ? 'border-emerald-500/50 bg-emerald-500/15 text-emerald-300'
          : 'border-white/10 text-white/60 hover:text-white hover:border-white/25 hover:bg-white/5',
        className,
      ].join(' ')}
    >
      {copied ? (
        <>
          <Check className="w-3.5 h-3.5" />
          <span>Link Copied!</span>
        </>
      ) : (
        <>
          <Share2 className="w-3.5 h-3.5" />
          <span>Share</span>
        </>
      )}
    </button>
  );
}
