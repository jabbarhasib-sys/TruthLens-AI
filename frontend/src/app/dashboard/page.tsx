'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Shield, Search, ImageIcon, AlertTriangle, CheckCircle, LogOut, ArrowUpRight, Clock, Database, User, Crown } from 'lucide-react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { DashboardStatsSkeleton, DashboardHistorySkeleton } from '@/components/ui/skeleton';

interface UserProfile {
  id: number;
  email: string;
  full_name: string | null;
  role: string;
}

interface HistoryItem {
  id: string;
  type: string;
  query: string;
  status: string;
  trust_score: number | null;
  risk_level: string | null;
  created_at: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);

  useEffect(() => {
    // Auth guard
    if (!api.isAuthenticated()) {
      router.push('/login');
      return;
    }

    const controller = new AbortController();

    const fetchData = async () => {
      try {
        const [data, profile] = await Promise.all([
          api.get<HistoryItem[]>('/history', controller.signal),
          api.get<UserProfile>('/users/me', controller.signal).catch(() => null),
        ]);
        setHistory(data);
        setUserProfile(profile);
      } catch (err: any) {
        if (err.name === 'AbortError') return;
        if (err.status === 401) {
          api.clearToken();
          router.push('/login');
        } else {
          setError('Failed to load analysis history.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    return () => controller.abort();
  }, [router]);

  const handleLogout = () => {
    api.clearToken();
    router.push('/');
  };

  // Stats calculation
  const totalScans = history.length;
  const criticalCount = history.filter(item => item.risk_level === 'CRITICAL' || item.risk_level === 'HIGH').length;
  const safeCount = history.filter(item => item.risk_level === 'LOW').length;
  const avgTrustScore = totalScans > 0 
    ? Math.round(history.reduce((acc, curr) => acc + (curr.trust_score || 0), 0) / totalScans)
    : 0;

  return (
    <main className="min-h-screen bg-[#030712] text-white">
      {/* Navbar */}
      <nav className="border-b border-white/10 bg-white/[0.02] px-6 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500">
            <Shield className="w-4 h-4 text-white" />
          </div>
          <span className="text-lg font-bold tracking-tight text-white">
            Truth<span className="text-emerald-400">Lens</span>
          </span>
        </Link>
        <div className="flex items-center gap-2">
          {userProfile?.role === 'admin' && (
            <Link
              href="/admin"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-xs text-amber-400 hover:bg-amber-500/20 transition-all"
            >
              <Crown className="w-3.5 h-3.5" />
              Admin
            </Link>
          )}
          <Link
            href="/profile"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-white/10 text-xs text-white/60 hover:text-white hover:bg-white/5 transition-all"
          >
            <User className="w-3.5 h-3.5" />
            {userProfile?.full_name || userProfile?.email?.split('@')[0] || 'Profile'}
          </Link>
          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-white/10 text-xs text-white/60 hover:text-white hover:bg-white/5 transition-all cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Sign out</span>
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-6 py-10 space-y-10">
        
        {/* Header Title */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight">Trust Verification Dashboard</h1>
            <p className="text-white/50 text-sm mt-1">Submit new materials for deep analysis or inspect past reports.</p>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/verify/news"
              className="flex items-center gap-1.5 px-5 py-2.5 rounded-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 font-semibold text-xs transition-all shadow-lg shadow-emerald-500/25"
            >
              <Search className="w-3.5 h-3.5" />
              Verify News Claim
            </Link>
            <Link
              href="/verify/image"
              className="flex items-center gap-1.5 px-5 py-2.5 rounded-full border border-white/10 hover:bg-white/5 font-semibold text-xs transition-all"
            >
              <ImageIcon className="w-3.5 h-3.5" />
              Verify Image
            </Link>
          </div>
        </div>

        {/* Stats Grid */}
        {loading ? (
          <DashboardStatsSkeleton />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
            {/* Card 1 */}
            <div className="glass-card p-6 border border-white/10 bg-white/5 rounded-2xl relative overflow-hidden">
              <div className="absolute top-4 right-4 text-emerald-400/20"><Database className="w-12 h-12" /></div>
              <div className="text-xs text-white/55 font-medium uppercase tracking-wider">Total Claims Scanned</div>
              <div className="text-3xl font-bold mt-2">{totalScans}</div>
            </div>
            {/* Card 2 */}
            <div className="glass-card p-6 border border-white/10 bg-white/5 rounded-2xl relative overflow-hidden">
              <div className="absolute top-4 right-4 text-emerald-400/20"><CheckCircle className="w-12 h-12" /></div>
              <div className="text-xs text-white/55 font-medium uppercase tracking-wider">Average Trust Score</div>
              <div className="text-3xl font-bold mt-2 text-emerald-400">{avgTrustScore}%</div>
            </div>
            {/* Card 3 */}
            <div className="glass-card p-6 border border-white/10 bg-white/5 rounded-2xl relative overflow-hidden">
              <div className="absolute top-4 right-4 text-red-400/20"><AlertTriangle className="w-12 h-12" /></div>
              <div className="text-xs text-white/55 font-medium uppercase tracking-wider">Critical/High Risk</div>
              <div className="text-3xl font-bold mt-2 text-red-400">{criticalCount}</div>
            </div>
            {/* Card 4 */}
            <div className="glass-card p-6 border border-white/10 bg-white/5 rounded-2xl relative overflow-hidden">
              <div className="absolute top-4 right-4 text-teal-400/20"><Shield className="w-12 h-12" /></div>
              <div className="text-xs text-white/55 font-medium uppercase tracking-wider">Low Risk Verified</div>
              <div className="text-3xl font-bold mt-2 text-teal-400">{safeCount}</div>
            </div>
          </div>
        )}

        {/* History Table */}
        <div className="glass-card border border-white/10 bg-white/5 rounded-2xl overflow-hidden">
          <div className="p-6 border-b border-white/10 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-emerald-400" />
              <h3 className="font-bold text-lg">Analysis History</h3>
            </div>
            <span className="text-xs text-white/40">{totalScans} records found</span>
          </div>

          {loading ? (
            <DashboardHistorySkeleton />
          ) : error ? (
            <div className="p-12 text-center text-sm text-red-400">{error}</div>
          ) : history.length === 0 ? (
            <div className="p-20 text-center space-y-4">
              <p className="text-white/40 text-sm">You haven&apos;t run any claim checks yet.</p>
              <Link
                href="/verify/news"
                className="inline-flex items-center gap-1 px-4 py-2 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-semibold"
              >
                Start your first verification
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-sm">
                <thead>
                  <tr className="border-b border-white/10 text-white/40 text-xs uppercase font-semibold">
                    <th className="px-6 py-4">Verification Type</th>
                    <th className="px-6 py-4">Search Context</th>
                    <th className="px-6 py-4">Created Date</th>
                    <th className="px-6 py-4">Trust Score</th>
                    <th className="px-6 py-4">Risk Level</th>
                    <th className="px-6 py-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {history.map((item) => (
                    <tr key={item.id} className="hover:bg-white/[0.02] transition-colors">
                      <td className="px-6 py-4 font-semibold">
                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          item.type === 'news' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-teal-500/10 text-teal-400 border border-teal-500/20'
                        }`}>
                          {item.type === 'news' ? 'News Claim' : 'Image Scan'}
                        </span>
                      </td>
                      <td className="px-6 py-4 max-w-xs truncate font-medium text-white/80">{item.query}</td>
                      <td className="px-6 py-4 text-white/55">
                        {new Date(item.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4">
                        {item.status === 'completed' ? (
                          <span className="font-bold text-white">{item.trust_score}%</span>
                        ) : (
                          <span className="text-white/30 italic">Processing</span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        {item.status === 'completed' ? (
                          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold uppercase tracking-wider ${
                            item.risk_level === 'LOW' ? 'bg-emerald-500/10 text-emerald-400' :
                            item.risk_level === 'MEDIUM' ? 'bg-yellow-500/10 text-yellow-400' :
                            item.risk_level === 'HIGH' ? 'bg-orange-500/10 text-orange-400' :
                            'bg-red-500/10 text-red-400'
                          }`}>
                            {item.risk_level}
                          </span>
                        ) : (
                          <span className="text-white/30 italic">{item.status}</span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <Link
                          href={`/report/${item.id}`}
                          className="inline-flex items-center gap-0.5 text-xs text-emerald-400 hover:text-emerald-300 font-semibold"
                        >
                          View Report
                          <ArrowUpRight className="w-3.5 h-3.5" />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

      </div>
    </main>
  );
}
