'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  Shield, User, Mail, Lock, Save, ArrowLeft,
  CheckCircle, AlertCircle, Loader2, Clock, Crown, Activity
} from 'lucide-react';
import Link from 'next/link';
import { api } from '@/lib/api';

interface UserProfile {
  id: number;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  last_login: string | null;
  created_at: string;
}

export default function ProfilePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  // Form state
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  useEffect(() => {
    if (!api.isAuthenticated()) {
      router.push('/login');
      return;
    }

    api.get<UserProfile>('/users/me')
      .then((data) => {
        setProfile(data);
        setFullName(data.full_name || '');
        setEmail(data.email || '');
      })
      .catch(() => {
        api.clearToken();
        router.push('/login');
      })
      .finally(() => setLoading(false));
  }, [router]);

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (newPassword && newPassword !== confirmPassword) {
      setError('New passwords do not match.');
      return;
    }

    setSaving(true);
    try {
      const payload: Record<string, string> = {};
      if (fullName !== profile?.full_name) payload.full_name = fullName;
      if (email !== profile?.email) payload.email = email;
      if (newPassword) {
        payload.current_password = currentPassword;
        payload.new_password = newPassword;
      }

      const updated = await api.patch<UserProfile>('/users/me', payload);
      setProfile(updated);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      setSuccess('Profile updated successfully!');
      setTimeout(() => setSuccess(''), 4000);
    } catch (err: any) {
      setError(err.message || 'Failed to update profile.');
    } finally {
      setSaving(false);
    }
  };

  const formatDate = (dt: string | null) => {
    if (!dt) return 'Never';
    return new Date(dt).toLocaleString('en-US', {
      dateStyle: 'medium',
      timeStyle: 'short',
    });
  };

  const getInitials = (name: string | null, email: string) => {
    if (name) return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    return email.slice(0, 2).toUpperCase();
  };

  return (
    <main className="min-h-screen bg-[#030712] text-white">
      {/* Navbar */}
      <nav className="border-b border-white/10 bg-white/[0.02] px-6 py-4 flex items-center justify-between">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500">
            <Shield className="w-4 h-4 text-white" />
          </div>
          <span className="text-lg font-bold tracking-tight text-white">
            Truth<span className="text-emerald-400">Lens</span>
          </span>
        </Link>
        <Link
          href="/dashboard"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-white/10 text-xs text-white/60 hover:text-white hover:bg-white/5 transition-all"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to Dashboard
        </Link>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-10 space-y-8">

        {/* Page Header */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-3xl font-extrabold tracking-tight">My Profile</h1>
          <p className="text-white/50 text-sm mt-1">Manage your account information and security settings.</p>
        </motion.div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1, 2, 3].map(i => (
              <div key={i} className="skeleton h-32 rounded-2xl" />
            ))}
          </div>
        ) : profile && (
          <>
            {/* Profile Overview Card */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="glass-card p-6 border border-white/10 bg-white/5 rounded-2xl flex flex-col md:flex-row items-center md:items-start gap-6"
            >
              {/* Avatar */}
              <div className="flex-shrink-0 w-20 h-20 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-2xl font-bold shadow-lg shadow-emerald-500/20">
                {getInitials(profile.full_name, profile.email)}
              </div>
              <div className="flex-1 text-center md:text-left">
                <div className="flex flex-col md:flex-row md:items-center gap-2 mb-1">
                  <h2 className="text-xl font-bold">{profile.full_name || profile.email.split('@')[0]}</h2>
                  <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                    profile.role === 'admin'
                      ? 'bg-amber-500/15 text-amber-400 border border-amber-500/20'
                      : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  }`}>
                    {profile.role === 'admin' && <Crown className="w-3 h-3" />}
                    {profile.role.toUpperCase()}
                  </span>
                  <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                    profile.is_active
                      ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20'
                      : 'bg-red-500/10 text-red-400 border border-red-500/20'
                  }`}>
                    <Activity className="w-3 h-3" />
                    {profile.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <p className="text-white/50 text-sm">{profile.email}</p>
              </div>
              <div className="grid grid-cols-2 gap-4 text-center flex-shrink-0">
                <div className="bg-white/5 rounded-xl p-3">
                  <div className="text-xs text-white/40 mb-1 flex items-center justify-center gap-1">
                    <Clock className="w-3 h-3" /> Joined
                  </div>
                  <div className="text-xs font-semibold text-white/80">{formatDate(profile.created_at)}</div>
                </div>
                <div className="bg-white/5 rounded-xl p-3">
                  <div className="text-xs text-white/40 mb-1 flex items-center justify-center gap-1">
                    <Clock className="w-3 h-3" /> Last Login
                  </div>
                  <div className="text-xs font-semibold text-white/80">{formatDate(profile.last_login)}</div>
                </div>
              </div>
            </motion.div>

            {/* Edit Form */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="glass-card p-8 border border-white/10 bg-white/5 rounded-2xl"
            >
              <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                <User className="w-5 h-5 text-emerald-400" />
                Edit Profile
              </h3>

              {success && (
                <div className="mb-5 flex items-center gap-2 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm">
                  <CheckCircle className="w-4 h-4 flex-shrink-0" />
                  {success}
                </div>
              )}
              {error && (
                <div className="mb-5 flex items-center gap-2 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  {error}
                </div>
              )}

              <form onSubmit={handleSaveProfile} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Full Name */}
                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-white/70 uppercase tracking-wider block">Full Name</label>
                    <div className="relative">
                      <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-white/30">
                        <User className="w-4 h-4" />
                      </span>
                      <input
                        type="text"
                        placeholder="Your full name"
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-emerald-500/50 focus:outline-none transition-all text-sm text-white"
                      />
                    </div>
                  </div>

                  {/* Email */}
                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-white/70 uppercase tracking-wider block">Email Address</label>
                    <div className="relative">
                      <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-white/30">
                        <Mail className="w-4 h-4" />
                      </span>
                      <input
                        type="email"
                        placeholder="email@example.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-emerald-500/50 focus:outline-none transition-all text-sm text-white"
                      />
                    </div>
                  </div>
                </div>

                {/* Password Section */}
                <div className="pt-4 border-t border-white/10">
                  <h4 className="text-sm font-semibold text-white/70 mb-4 flex items-center gap-2">
                    <Lock className="w-4 h-4" />
                    Change Password <span className="text-white/30 font-normal">(leave blank to keep current)</span>
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <label className="text-xs font-semibold text-white/70 uppercase tracking-wider block">Current Password</label>
                      <input
                        type="password"
                        placeholder="••••••••"
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-emerald-500/50 focus:outline-none transition-all text-sm text-white"
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-semibold text-white/70 uppercase tracking-wider block">New Password</label>
                      <input
                        type="password"
                        placeholder="••••••••"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-emerald-500/50 focus:outline-none transition-all text-sm text-white"
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-semibold text-white/70 uppercase tracking-wider block">Confirm Password</label>
                      <input
                        type="password"
                        placeholder="••••••••"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-emerald-500/50 focus:outline-none transition-all text-sm text-white"
                      />
                    </div>
                  </div>
                </div>

                <div className="flex justify-end pt-2">
                  <button
                    type="submit"
                    disabled={saving}
                    className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold text-sm transition-all shadow-lg shadow-emerald-500/20 disabled:opacity-70 disabled:cursor-not-allowed cursor-pointer"
                  >
                    {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                    {saving ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              </form>
            </motion.div>

            {/* Admin Panel Link */}
            {profile.role === 'admin' && (
              <motion.div
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 }}
                className="glass-card p-6 border border-amber-500/20 bg-amber-500/5 rounded-2xl flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center">
                    <Crown className="w-5 h-5 text-amber-400" />
                  </div>
                  <div>
                    <p className="font-bold text-amber-300">Admin Access</p>
                    <p className="text-xs text-white/50">You have full administrative privileges</p>
                  </div>
                </div>
                <Link
                  href="/admin"
                  className="px-5 py-2.5 rounded-xl bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/20 text-amber-400 text-sm font-semibold transition-all"
                >
                  Open Admin Panel →
                </Link>
              </motion.div>
            )}
          </>
        )}
      </div>
    </main>
  );
}
