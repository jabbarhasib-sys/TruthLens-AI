'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield, Users, BarChart3, ArrowLeft, Crown, Activity,
  Search, UserCheck, UserX, RotateCcw, Trash2, Edit3,
  AlertTriangle, CheckCircle, Loader2, X, ChevronDown,
  Database, TrendingUp, Clock
} from 'lucide-react';
import Link from 'next/link';
import { api } from '@/lib/api';

interface User {
  id: number;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  last_login: string | null;
  created_at: string;
}

interface AdminStats {
  total_users: number;
  active_users: number;
  inactive_users: number;
  admin_users: number;
  total_analyses: number;
  completed_analyses: number;
  pending_analyses: number;
}

interface EditModal {
  user: User;
  fullName: string;
  role: string;
  isActive: boolean;
}

export default function AdminPage() {
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);
  const [editModal, setEditModal] = useState<EditModal | null>(null);
  const [editSaving, setEditSaving] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState<User | null>(null);
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  const showToast = (msg: string, type: 'success' | 'error' = 'success') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 4000);
  };

  const loadData = useCallback(async () => {
    try {
      const [usersData, statsData] = await Promise.all([
        api.get<User[]>('/admin/users'),
        api.get<AdminStats>('/admin/stats'),
      ]);
      setUsers(usersData);
      setStats(statsData);
    } catch (err: any) {
      if (err.status === 401 || err.status === 403) {
        router.push('/dashboard');
      }
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    if (!api.isAuthenticated()) {
      router.push('/login');
      return;
    }
    loadData();
  }, [router, loadData]);

  const filteredUsers = users.filter(u => {
    const matchSearch =
      u.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (u.full_name || '').toLowerCase().includes(searchQuery.toLowerCase());
    const matchRole = roleFilter === 'all' || u.role === roleFilter;
    const matchStatus =
      statusFilter === 'all' ||
      (statusFilter === 'active' ? u.is_active : !u.is_active);
    return matchSearch && matchRole && matchStatus;
  });

  const handleToggleActive = async (user: User) => {
    setActionLoading(user.id);
    try {
      const updated = await api.patch<User>(`/admin/users/${user.id}`, {
        is_active: !user.is_active,
      });
      setUsers(prev => prev.map(u => u.id === updated.id ? updated : u));
      showToast(`${updated.email} ${updated.is_active ? 'activated' : 'deactivated'}.`);
    } catch (err: any) {
      showToast(err.message || 'Failed to update user.', 'error');
    } finally {
      setActionLoading(null);
    }
  };

  const handleResetPassword = async (user: User) => {
    setActionLoading(user.id);
    try {
      await api.post2(`/admin/users/${user.id}/reset-password`);
      showToast(`Password reset to default (123456) for ${user.email}.`);
    } catch (err: any) {
      showToast(err.message || 'Failed to reset password.', 'error');
    } finally {
      setActionLoading(null);
    }
  };

  const handleDeleteUser = async () => {
    if (!confirmDelete) return;
    setActionLoading(confirmDelete.id);
    try {
      await api.delete(`/admin/users/${confirmDelete.id}`);
      setUsers(prev => prev.filter(u => u.id !== confirmDelete.id));
      setStats(prev => prev ? { ...prev, total_users: prev.total_users - 1, active_users: confirmDelete.is_active ? prev.active_users - 1 : prev.active_users } : prev);
      showToast(`${confirmDelete.email} has been deleted.`);
    } catch (err: any) {
      showToast(err.message || 'Failed to delete user.', 'error');
    } finally {
      setActionLoading(null);
      setConfirmDelete(null);
    }
  };

  const handleSaveEdit = async () => {
    if (!editModal) return;
    setEditSaving(true);
    try {
      const updated = await api.patch<User>(`/admin/users/${editModal.user.id}`, {
        full_name: editModal.fullName,
        role: editModal.role,
        is_active: editModal.isActive,
      });
      setUsers(prev => prev.map(u => u.id === updated.id ? updated : u));
      showToast(`${updated.email} updated successfully.`);
      setEditModal(null);
    } catch (err: any) {
      showToast(err.message || 'Failed to update user.', 'error');
    } finally {
      setEditSaving(false);
    }
  };

  const formatDate = (dt: string | null) => {
    if (!dt) return '—';
    return new Date(dt).toLocaleDateString('en-US', { dateStyle: 'medium' });
  };

  const getInitials = (name: string | null, email: string) => {
    if (name) return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    return email.slice(0, 2).toUpperCase();
  };

  return (
    <main className="min-h-screen bg-[#030712] text-white">
      {/* Navbar */}
      <nav className="border-b border-white/10 bg-white/[0.02] px-6 py-4 flex items-center justify-between sticky top-0 z-10 backdrop-blur-md">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500">
            <Shield className="w-4 h-4 text-white" />
          </div>
          <span className="text-lg font-bold tracking-tight text-white">
            Truth<span className="text-emerald-400">Lens</span>
          </span>
        </Link>
        <div className="flex items-center gap-2">
          <span className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold">
            <Crown className="w-3 h-3" /> Admin Panel
          </span>
          <Link
            href="/dashboard"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-white/10 text-xs text-white/60 hover:text-white hover:bg-white/5 transition-all"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Dashboard
          </Link>
        </div>
      </nav>

      {/* Toast */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className={`fixed top-20 right-6 z-50 flex items-center gap-2 px-4 py-3 rounded-xl text-sm font-medium shadow-xl border ${
              toast.type === 'success'
                ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300'
                : 'bg-red-500/15 border-red-500/30 text-red-300'
            }`}
          >
            {toast.type === 'success' ? <CheckCircle className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
            {toast.msg}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Edit Modal */}
      <AnimatePresence>
        {editModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4"
            onClick={(e) => e.target === e.currentTarget && setEditModal(null)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="glass-elevated w-full max-w-md p-6 space-y-5"
            >
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-lg flex items-center gap-2">
                  <Edit3 className="w-5 h-5 text-emerald-400" />
                  Edit User
                </h3>
                <button onClick={() => setEditModal(null)} className="p-1 rounded-lg hover:bg-white/10 transition-colors text-white/60 cursor-pointer">
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="text-xs font-semibold text-white/60 uppercase tracking-wider block mb-1.5">Full Name</label>
                  <input
                    type="text"
                    value={editModal.fullName}
                    onChange={e => setEditModal({ ...editModal, fullName: e.target.value })}
                    className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-emerald-500/50 focus:outline-none text-sm text-white"
                    placeholder="User's full name"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-white/60 uppercase tracking-wider block mb-1.5">Role</label>
                  <div className="relative">
                    <select
                      value={editModal.role}
                      onChange={e => setEditModal({ ...editModal, role: e.target.value })}
                      className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-emerald-500/50 focus:outline-none text-sm text-white appearance-none cursor-pointer"
                    >
                      <option value="user" className="bg-gray-900">User</option>
                      <option value="admin" className="bg-gray-900">Admin</option>
                    </select>
                    <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40 pointer-events-none" />
                  </div>
                </div>
                <div>
                  <label className="text-xs font-semibold text-white/60 uppercase tracking-wider block mb-1.5">Status</label>
                  <div className="flex gap-3">
                    {[{ val: true, label: 'Active' }, { val: false, label: 'Inactive' }].map(({ val, label }) => (
                      <button
                        key={label}
                        type="button"
                        onClick={() => setEditModal({ ...editModal, isActive: val })}
                        className={`flex-1 py-3 rounded-xl text-sm font-semibold border transition-all cursor-pointer ${
                          editModal.isActive === val
                            ? val ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-400' : 'bg-red-500/15 border-red-500/40 text-red-400'
                            : 'bg-white/5 border-white/10 text-white/50 hover:border-white/20'
                        }`}
                      >
                        {label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  onClick={() => setEditModal(null)}
                  className="flex-1 py-3 rounded-xl border border-white/10 text-sm text-white/60 hover:text-white hover:bg-white/5 transition-all cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveEdit}
                  disabled={editSaving}
                  className="flex-1 py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold text-sm transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-70"
                >
                  {editSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                  {editSaving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Delete Confirmation Modal */}
      <AnimatePresence>
        {confirmDelete && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4"
            onClick={(e) => e.target === e.currentTarget && setConfirmDelete(null)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="glass-elevated w-full max-w-sm p-6 space-y-5"
            >
              <div className="text-center space-y-3">
                <div className="w-12 h-12 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto">
                  <Trash2 className="w-6 h-6 text-red-400" />
                </div>
                <h3 className="font-bold text-lg">Delete User?</h3>
                <p className="text-sm text-white/50">
                  This will permanently delete <strong className="text-white">{confirmDelete.email}</strong> and all their data. This action cannot be undone.
                </p>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setConfirmDelete(null)}
                  className="flex-1 py-3 rounded-xl border border-white/10 text-sm text-white/60 hover:text-white hover:bg-white/5 transition-all cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteUser}
                  disabled={actionLoading === confirmDelete.id}
                  className="flex-1 py-3 rounded-xl bg-red-600/80 hover:bg-red-600 text-white font-semibold text-sm transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-70"
                >
                  {actionLoading === confirmDelete.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
                  Delete
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="max-w-7xl mx-auto px-6 py-10 space-y-8">

        {/* Page Header */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <h1 className="text-3xl font-extrabold tracking-tight flex items-center gap-3">
            <span className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/20">
              <Crown className="w-6 h-6 text-amber-400" />
            </span>
            Admin Dashboard
          </h1>
          <p className="text-white/50 text-sm mt-1 ml-14">Monitor users, manage access, and view system-wide analytics.</p>
        </motion.div>

        {/* Stats Grid */}
        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map(i => <div key={i} className="skeleton h-28 rounded-2xl" />)}
          </div>
        ) : stats && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-4"
          >
            {[
              { label: 'Total Users', value: stats.total_users, icon: Users, color: 'emerald', sub: `${stats.admin_users} admin(s)` },
              { label: 'Active Users', value: stats.active_users, icon: UserCheck, color: 'teal', sub: `${stats.inactive_users} inactive` },
              { label: 'Total Analyses', value: stats.total_analyses, icon: Database, color: 'blue', sub: `${stats.completed_analyses} completed` },
              { label: 'Pending Analyses', value: stats.pending_analyses, icon: TrendingUp, color: 'amber', sub: `${stats.total_analyses > 0 ? Math.round((stats.completed_analyses/stats.total_analyses)*100) : 0}% complete rate` },
            ].map(({ label, value, icon: Icon, color, sub }) => (
              <div key={label} className={`glass-card p-5 border border-white/10 bg-white/5 rounded-2xl relative overflow-hidden`}>
                <div className={`absolute top-4 right-4 text-${color}-400/15`}>
                  <Icon className="w-10 h-10" />
                </div>
                <div className="text-xs text-white/50 font-medium uppercase tracking-wider">{label}</div>
                <div className={`text-3xl font-bold mt-2 text-${color}-400`}>{value}</div>
                <div className="text-xs text-white/30 mt-1">{sub}</div>
              </div>
            ))}
          </motion.div>
        )}

        {/* Users Table */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="glass-card border border-white/10 bg-white/5 rounded-2xl overflow-hidden"
        >
          {/* Table Header */}
          <div className="p-6 border-b border-white/10">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <Users className="w-5 h-5 text-emerald-400" />
                <h3 className="font-bold text-lg">User Management</h3>
                <span className="ml-1 text-xs bg-white/10 px-2 py-0.5 rounded-full text-white/60">{filteredUsers.length} shown</span>
              </div>
              {/* Filters */}
              <div className="flex flex-wrap items-center gap-3">
                {/* Search */}
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-white/30" />
                  <input
                    type="text"
                    placeholder="Search users..."
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    className="pl-9 pr-4 py-2 rounded-xl bg-white/5 border border-white/10 focus:border-emerald-500/50 focus:outline-none text-sm text-white w-52"
                  />
                </div>
                {/* Role Filter */}
                <div className="relative">
                  <select
                    value={roleFilter}
                    onChange={e => setRoleFilter(e.target.value)}
                    className="pl-3 pr-8 py-2 rounded-xl bg-white/5 border border-white/10 focus:border-emerald-500/50 focus:outline-none text-sm text-white appearance-none cursor-pointer"
                  >
                    <option value="all" className="bg-gray-900">All Roles</option>
                    <option value="user" className="bg-gray-900">Users</option>
                    <option value="admin" className="bg-gray-900">Admins</option>
                  </select>
                  <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-white/40 pointer-events-none" />
                </div>
                {/* Status Filter */}
                <div className="relative">
                  <select
                    value={statusFilter}
                    onChange={e => setStatusFilter(e.target.value)}
                    className="pl-3 pr-8 py-2 rounded-xl bg-white/5 border border-white/10 focus:border-emerald-500/50 focus:outline-none text-sm text-white appearance-none cursor-pointer"
                  >
                    <option value="all" className="bg-gray-900">All Status</option>
                    <option value="active" className="bg-gray-900">Active</option>
                    <option value="inactive" className="bg-gray-900">Inactive</option>
                  </select>
                  <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-white/40 pointer-events-none" />
                </div>
              </div>
            </div>
          </div>

          {/* Table Body */}
          {loading ? (
            <div className="p-6 space-y-3">
              {[1, 2, 3, 4, 5].map(i => <div key={i} className="skeleton h-14 rounded-xl" />)}
            </div>
          ) : filteredUsers.length === 0 ? (
            <div className="p-16 text-center text-white/40 text-sm">No users match your filters.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-sm">
                <thead>
                  <tr className="border-b border-white/10 text-white/40 text-xs uppercase font-semibold">
                    <th className="px-6 py-4">User</th>
                    <th className="px-6 py-4">Role</th>
                    <th className="px-6 py-4">Status</th>
                    <th className="px-6 py-4">Joined</th>
                    <th className="px-6 py-4">Last Login</th>
                    <th className="px-6 py-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {filteredUsers.map((user) => (
                    <tr key={user.id} className="hover:bg-white/[0.025] transition-colors group">
                      {/* User */}
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className={`w-9 h-9 rounded-xl flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                            user.role === 'admin'
                              ? 'bg-amber-500/15 text-amber-400 border border-amber-500/20'
                              : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          }`}>
                            {getInitials(user.full_name, user.email)}
                          </div>
                          <div>
                            <div className="font-semibold text-white text-sm">
                              {user.full_name || <span className="text-white/40 italic">No name</span>}
                            </div>
                            <div className="text-xs text-white/40">{user.email}</div>
                          </div>
                        </div>
                      </td>
                      {/* Role */}
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                          user.role === 'admin'
                            ? 'bg-amber-500/15 text-amber-400 border border-amber-500/20'
                            : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        }`}>
                          {user.role === 'admin' && <Crown className="w-3 h-3" />}
                          {user.role}
                        </span>
                      </td>
                      {/* Status */}
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                          user.is_active
                            ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20'
                            : 'bg-red-500/10 text-red-400 border border-red-500/20'
                        }`}>
                          <Activity className="w-3 h-3" />
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      {/* Joined */}
                      <td className="px-6 py-4 text-white/50 text-xs">{formatDate(user.created_at)}</td>
                      {/* Last Login */}
                      <td className="px-6 py-4 text-white/50 text-xs">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatDate(user.last_login)}
                        </span>
                      </td>
                      {/* Actions */}
                      <td className="px-6 py-4">
                        <div className="flex items-center justify-end gap-1 opacity-70 group-hover:opacity-100 transition-opacity">
                          {/* Edit */}
                          <button
                            onClick={() => setEditModal({ user, fullName: user.full_name || '', role: user.role, isActive: user.is_active })}
                            title="Edit user"
                            className="p-2 rounded-lg hover:bg-white/10 text-white/60 hover:text-white transition-all cursor-pointer"
                          >
                            <Edit3 className="w-3.5 h-3.5" />
                          </button>
                          {/* Toggle Active */}
                          <button
                            onClick={() => handleToggleActive(user)}
                            disabled={actionLoading === user.id}
                            title={user.is_active ? 'Deactivate' : 'Activate'}
                            className={`p-2 rounded-lg transition-all cursor-pointer disabled:opacity-50 ${
                              user.is_active
                                ? 'hover:bg-red-500/10 text-red-400/60 hover:text-red-400'
                                : 'hover:bg-emerald-500/10 text-emerald-400/60 hover:text-emerald-400'
                            }`}
                          >
                            {actionLoading === user.id ? (
                              <Loader2 className="w-3.5 h-3.5 animate-spin" />
                            ) : user.is_active ? (
                              <UserX className="w-3.5 h-3.5" />
                            ) : (
                              <UserCheck className="w-3.5 h-3.5" />
                            )}
                          </button>
                          {/* Reset Password */}
                          <button
                            onClick={() => handleResetPassword(user)}
                            disabled={actionLoading === user.id}
                            title="Reset to default password (123456)"
                            className="p-2 rounded-lg hover:bg-amber-500/10 text-amber-400/60 hover:text-amber-400 transition-all cursor-pointer disabled:opacity-50"
                          >
                            <RotateCcw className="w-3.5 h-3.5" />
                          </button>
                          {/* Delete */}
                          <button
                            onClick={() => setConfirmDelete(user)}
                            disabled={actionLoading === user.id}
                            title="Delete user"
                            className="p-2 rounded-lg hover:bg-red-500/10 text-white/30 hover:text-red-400 transition-all cursor-pointer disabled:opacity-50"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </motion.div>

      </div>
    </main>
  );
}
