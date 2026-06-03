'use client';
import { useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';

export default function Login() {
  const [email, setEmail]     = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]     = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      const r = await api.auth.login(email, password);
      localStorage.setItem('token', r.access_token);
      localStorage.setItem('refresh_token', r.refresh_token);
      localStorage.setItem('user', JSON.stringify(r.user));
      window.location.href = '/dashboard';
    } catch (err: any) {
      setError(err.message || 'Login failed');
    }
    setLoading(false);
  };

  return (
    <div style={{ background:'#0f1117', minHeight:'100vh', display:'flex',
                  alignItems:'center', justifyContent:'center', fontFamily:'system-ui' }}>
      <div style={{ background:'#1a1d27', borderRadius:16, padding:'40px 44px', width:380 }}>
        <div style={{ textAlign:'center', marginBottom:32 }}>
          <div style={{ fontSize:40 }}>🧠</div>
          <h1 style={{ color:'#e2e8f0', fontSize:24, fontWeight:700, margin:'12px 0 4px' }}>Welcome back</h1>
          <p style={{ color:'#64748b', fontSize:14 }}>Sign in to AI Memory Engine</p>
        </div>
        <form onSubmit={submit} style={{ display:'flex', flexDirection:'column', gap:16 }}>
          <input type="email" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)}
            required style={inputStyle} />
          <input type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)}
            required style={inputStyle} />
          {error && <div style={{ color:'#ef4444', fontSize:13 }}>{error}</div>}
          <button type="submit" disabled={loading}
            style={{ background:'#6c63ff', color:'white', border:'none', padding:'12px',
                     borderRadius:8, cursor:'pointer', fontWeight:600, fontSize:15 }}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <p style={{ textAlign:'center', color:'#64748b', fontSize:13, marginTop:20 }}>
          Don&apos;t have an account?{' '}
          <Link href="/register" style={{ color:'#a78bfa', textDecoration:'none' }}>Sign up free</Link>
        </p>
      </div>
    </div>
  );
}

const inputStyle: React.CSSProperties = {
  padding:'11px 14px', background:'#252836', color:'#e2e8f0',
  border:'1px solid #2e3148', borderRadius:8, fontSize:14, outline:'none',
};
