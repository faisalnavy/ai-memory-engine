'use client';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

interface Stats { files: number; functions: number; sessions: number; decisions: number; tokens_saved: number; }

export default function Dashboard() {
  const [stats, setStats]     = useState<Stats | null>(null);
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token') || '';
    const orgId = localStorage.getItem('org_id') || '';
    if (!token) { window.location.href = '/login'; return; }

    api.projects.list(orgId, token)
      .then(r => { setProjects(r.projects); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div style={{ background:'#0f1117', minHeight:'100vh', color:'#e2e8f0', padding:'40px 60px', fontFamily:'system-ui' }}>
      <h1 style={{ fontSize:28, fontWeight:700, marginBottom:8 }}>Dashboard</h1>
      <p style={{ color:'#64748b', marginBottom:40 }}>Your AI memory projects</p>

      {/* Aggregate stats */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:16, marginBottom:40 }}>
        {[['📁','Projects', projects.length],
          ['📄','Total Files','—'],
          ['⚡','Functions','—'],
          ['💡','Decisions','—'],
          ['🎯','Tokens Saved','—']].map(([icon,label,val]) => (
          <div key={label as string} style={{ background:'#1a1d27', borderRadius:12, padding:'20px 16px', textAlign:'center' }}>
            <div style={{ fontSize:24 }}>{icon}</div>
            <div style={{ fontSize:26, fontWeight:700, color:'#a78bfa', margin:'8px 0' }}>{val}</div>
            <div style={{ fontSize:12, color:'#64748b' }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Projects list */}
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:20 }}>
        <h2 style={{ fontSize:18, fontWeight:600 }}>Your Projects</h2>
        <button onClick={() => {/* open create modal */}}
          style={{ background:'#6c63ff', color:'white', border:'none', padding:'9px 20px',
                   borderRadius:8, cursor:'pointer', fontWeight:600 }}>
          + New Project
        </button>
      </div>

      {loading ? (
        <div style={{ color:'#64748b' }}>Loading...</div>
      ) : projects.length === 0 ? (
        <div style={{ background:'#1a1d27', borderRadius:12, padding:'48px', textAlign:'center' }}>
          <div style={{ fontSize:48, marginBottom:16 }}>🧠</div>
          <h3 style={{ color:'#a78bfa', marginBottom:8 }}>No projects yet</h3>
          <p style={{ color:'#64748b', marginBottom:24 }}>Create your first project to start saving tokens.</p>
          <button style={{ background:'#6c63ff', color:'white', border:'none', padding:'12px 28px',
                           borderRadius:8, cursor:'pointer', fontWeight:600 }}>
            Create Project
          </button>
        </div>
      ) : (
        <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
          {projects.map((p: any) => (
            <div key={p.id} style={{ background:'#1a1d27', borderRadius:12, padding:'20px 24px',
                                      display:'flex', alignItems:'center', gap:20, cursor:'pointer' }}
                 onClick={() => window.location.href = `/projects/${p.id}`}>
              <div style={{ fontSize:28 }}>📁</div>
              <div style={{ flex:1 }}>
                <div style={{ fontWeight:600, marginBottom:4 }}>{p.name}</div>
                <div style={{ fontSize:12, color:'#64748b' }}>{p.language} · {p.framework || 'No framework'}</div>
              </div>
              <div style={{ color:'#6c63ff', fontSize:20 }}>→</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
