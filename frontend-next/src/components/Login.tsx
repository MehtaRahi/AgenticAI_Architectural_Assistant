'use client';
import React, { useState } from 'react';

export default function Login({ onLogin }: { onLogin: () => void }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email && password) {
      onLogin();
    }
  };

  return (
    <div className="min-h-screen gradient-bg flex items-center justify-center relative overflow-hidden">
      {/* Ambient glow orbs */}
      <div className="glow-orb" style={{ width: 600, height: 600, background: '#6366f1', top: '-10%', left: '-10%' }} />
      <div className="glow-orb" style={{ width: 500, height: 500, background: '#8b5cf6', bottom: '-15%', right: '-5%' }} />
      <div className="glow-orb" style={{ width: 300, height: 300, background: '#06b6d4', top: '50%', left: '60%' }} />

      <div className="relative z-10 w-full max-w-md px-6">
        {/* Logo & Title */}
        <div className="text-center mb-10 fade-in">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-6" style={{ background: 'var(--accent-gradient)', boxShadow: '0 8px 32px var(--accent-glow)' }}>
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>
            ArchStudio<span style={{ color: 'var(--accent-primary)' }}> AI</span>
          </h1>
          <p className="mt-2 text-sm" style={{ color: 'var(--text-muted)' }}>
            Intelligent Architectural Design Assistant
          </p>
        </div>

        {/* Login Card */}
        <div className="glass-strong rounded-2xl p-8 slide-up" style={{ boxShadow: 'var(--shadow-lg)' }}>
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="field-label">Email</label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="input-field"
                placeholder="you@studio.com"
                required
              />
            </div>
            <div>
              <label className="field-label">Password</label>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="input-field"
                placeholder="••••••••••"
                required
              />
            </div>

            <button type="submit" className="btn-primary w-full text-center" style={{ padding: '14px 24px' }}>
              Sign In
            </button>

            <div className="flex items-center gap-4 py-1">
              <div className="flex-1 h-px" style={{ background: 'var(--border-subtle)' }} />
              <span className="text-xs" style={{ color: 'var(--text-muted)' }}>or</span>
              <div className="flex-1 h-px" style={{ background: 'var(--border-subtle)' }} />
            </div>

            <button
              type="button"
              onClick={onLogin}
              className="btn-ghost w-full text-center"
              style={{ padding: '12px 24px' }}
            >
              Continue as Guest
            </button>
          </form>
        </div>

        <p className="text-center mt-8 text-xs" style={{ color: 'var(--text-muted)' }}>
          NBC India Compliant · ADA Standards · AI-Powered Layout Engine
        </p>
      </div>
    </div>
  );
}
