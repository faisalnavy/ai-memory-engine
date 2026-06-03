import React, { useState, useEffect, useCallback } from 'react';
import { api } from './api';
import './App.css';

// ── Types ─────────────────────────────────────────────────────────────────────
interface Stats { file_memory: number; function_memory: number; knowledge_graph: number; decision_memory: number; session_memory: number; }
interface Dna   { name: string; language: string; framework: string; architecture: string; }
type Page = 'dashboard' | 'projects' | 'memory' | 'sessions' | 'decisions' | 'analytics';

// ── App ───────────────────────────────────────────────────────────────────────
export default function App() {
  const [page, setPage]               = useState<Page>('dashboard');
  const [projectPath, setProjectPath] = useState('');
  const [stats, setStats]             = useState<Stats | null>(null);
  const [dna, setDna]                 = useState<Dna | null>(null);
  const [log, setLog]                 = useState<string[]>([]);
  const [busy, setBusy]               = useState(false);
  const [query, setQuery]             = useState('');
  const [context, setContext]         = useState('');
  const [savings, setSavings]         = useState<any>(null);
  const [projects, setProjects]       = useState<string[]>([]);
  const [sessions, setSessions]       = useState<any[]>([]);
  const [decisions, setDecisions]     = useState<any[]>([]);
  const [edges, setEdges]             = useState<any[]>([]);

  const addLog = (msg: string) => setLog(l => [...l.slice(-200), msg]);

  const loadStats = useCallback(async () => {
    if (!projectPath) return;
    try {
      const r = await api.stats(projectPath);
      setStats(r.stats); setDna(r.dna);
    } catch {}
  }, [projectPath]);

  useEffect(() => { loadStats(); }, [loadStats]);
  useEffect(() => { api.projects().then(r => setProjects(r.projects)).catch(() => {}); }, []);

  const selectFolder = async () => {
    const ea = (window as any).electronAPI;
    if (ea) {
      const p = await ea.selectFolder();
      if (p) { setProjectPath(p); api.addProject(p).catch(() => {}); }
    } else {
      const p = prompt('Enter project path:');
      if (p) { setProjectPath(p); api.addProject(p).catch(() => {}); }
    }
  };

  const runInit = async () => {
    if (!projectPath) return;
    setBusy(true); addLog('Initializing...');
    try {
      const r = await api.init(projectPath);
      addLog(`OK Language: ${r.language} | Framework: ${r.framework || 'n/a'}`);
      addLog('Initialized! Now click Index.');
      setDna({ name: r.name, language: r.language, framework: r.framework, architecture: r.architecture });
    } catch (e: any) { addLog('ERROR: ' + e.message); }
    setBusy(false);
  };

  const runIndex = async () => {
    if (!projectPath) return;
    setBusy(true); addLog('Indexing all files...');
    try {
      const r = await api.index(projectPath);
      addLog(`OK Files: ${r.file_memory} | Functions: ${r.function_memory} | Edges: ${r.knowledge_graph}`);
      setStats(r); loadStats();
    } catch (e: any) { addLog('ERROR: ' + e.message); }
    setBusy(false);
  };

  const runAsk = async () => {
    if (!projectPath || !query) return;
    setBusy(true); addLog(`Query: "${query}"`);
    try {
      const r = await api.ask(projectPath, query);
      setContext(r.context);
      setSavings(r.report);
      addLog(`Savings: ${r.report.savings_pct}% (${r.report.original} → ${r.report.optimized} tokens)`);
    } catch (e: any) { addLog('ERROR: ' + e.message); }
    setBusy(false);
  };

  const loadSessions = async () => {
    if (!projectPath) return;
    const r = await api.sessions(projectPath).catch(() => ({ sessions: [] }));
    setSessions(r.sessions || []);
  };

  const loadDecisions = async () => {
    if (!projectPath) return;
    const r = await api.decisions(projectPath).catch(() => ({ decisions: [] }));
    setDecisions(r.decisions || []);
  };

  const loadGraph = async () => {
    if (!projectPath) return;
    const r = await api.graph(projectPath).catch(() => ({ edges: [] }));
    setEdges(r.edges || []);
  };

  useEffect(() => {
    if (page === 'sessions')  loadSessions();
    if (page === 'decisions') loadDecisions();
    if (page === 'memory')    loadGraph();
  }, [page, projectPath]);

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="app">
      {/* Sidebar */}
      <nav className="sidebar">
        <div className="sidebar-logo">🧠</div>
        <div className="sidebar-title">Memory<br/>Engine</div>
        {(['dashboard','projects','memory','sessions','decisions','analytics'] as Page[]).map(p => (
          <button key={p} className={`nav-btn ${page===p?'active':''}`} onClick={() => setPage(p)}>
            {pageIcon(p)} <span>{cap(p)}</span>
          </button>
        ))}
      </nav>

      {/* Main */}
      <main className="main">
        {/* Project bar */}
        <div className="project-bar">
          <button className="btn-browse" onClick={selectFolder}>📁 Browse</button>
          <input className="project-input" value={projectPath}
            onChange={e => setProjectPath(e.target.value)}
            placeholder="Select or type your project path..." />
          <button className="btn-action" onClick={runInit}  disabled={busy}>Init</button>
          <button className="btn-action" onClick={runIndex} disabled={busy}>Index</button>
          <button className="btn-action btn-update"
            onClick={() => { setBusy(true); api.update(projectPath).then(r => { addLog(`Updated: ${r.changed} files`); loadStats(); setBusy(false); }).catch(e => { addLog('ERROR: '+e.message); setBusy(false); }) }}
            disabled={busy}>Update</button>
        </div>

        {/* Pages */}
        {page === 'dashboard' && <Dashboard dna={dna} stats={stats} log={log} busy={busy} />}
        {page === 'projects'  && <Projects projects={projects} onSelect={p => { setProjectPath(p); setPage('dashboard'); }} />}
        {page === 'memory'    && <MemoryPage edges={edges} />}
        {page === 'sessions'  && <SessionsPage sessions={sessions} />}
        {page === 'decisions' && <DecisionsPage decisions={decisions} projectPath={projectPath} onAdd={loadDecisions} />}
        {page === 'analytics' && <Analytics stats={stats} savings={savings} query={query} setQuery={setQuery} runAsk={runAsk} context={context} busy={busy} />}
      </main>
    </div>
  );
}

// ── Sub-pages ─────────────────────────────────────────────────────────────────

function Dashboard({ dna, stats, log, busy }: any) {
  return (
    <div className="page">
      <h1>Dashboard</h1>
      {dna && (
        <div className="dna-card">
          <h2>{dna.name}</h2>
          <div className="dna-tags">
            <span className="tag">{dna.language}</span>
            {dna.framework && <span className="tag">{dna.framework}</span>}
            <span className="tag">{dna.architecture}</span>
          </div>
        </div>
      )}
      <div className="stat-grid">
        {[['📄','Files',stats?.file_memory],['⚡','Functions',stats?.function_memory],
          ['🕸️','Graph Edges',stats?.knowledge_graph],['💡','Decisions',stats?.decision_memory],
          ['📋','Sessions',stats?.session_memory]].map(([icon,label,val]) => (
          <div className="stat-card" key={label as string}>
            <div className="stat-icon">{icon}</div>
            <div className="stat-val">{val ?? '—'}</div>
            <div className="stat-label">{label}</div>
          </div>
        ))}
      </div>
      <div className="console">
        <div className="console-hdr">Console <span className={busy ? 'busy-dot' : 'idle-dot'} /></div>
        <div className="console-body">
          {log.length ? log.map((l,i) => <div key={i} className={l.startsWith('ERROR')?'log-err':l.startsWith('OK')?'log-ok':'log-dim'}>{l}</div>)
            : <div className="log-dim">Ready. Select a project and click Init → Index.</div>}
        </div>
      </div>
    </div>
  );
}

function Projects({ projects, onSelect }: any) {
  return (
    <div className="page">
      <h1>Recent Projects</h1>
      {projects.length === 0 && <p className="muted">No projects yet. Browse and initialize one.</p>}
      <div className="project-list">
        {projects.map((p: string) => (
          <div className="project-row" key={p} onClick={() => onSelect(p)}>
            <span className="project-icon">📁</span>
            <span className="project-path">{p}</span>
            <span className="project-arrow">→</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function MemoryPage({ edges }: any) {
  const fileEdges = edges.filter((e: any) => !e.source.includes('::') && !e.target.includes('::'));
  return (
    <div className="page">
      <h1>Dependency Graph</h1>
      <p className="muted">{fileEdges.length} file-level relationships found</p>
      <div className="graph-list">
        {fileEdges.slice(0,60).map((e: any, i: number) => (
          <div className="graph-row" key={i}>
            <span className="graph-src">{e.source}</span>
            <span className="graph-rel"> ──[{e.relationship}]──▶ </span>
            <span className="graph-tgt">{e.target}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function SessionsPage({ sessions }: any) {
  return (
    <div className="page">
      <h1>Session History</h1>
      <p className="muted">{sessions.length} sessions recorded</p>
      <div className="session-list">
        {sessions.map((s: any) => (
          <div className="session-row" key={s.id}>
            <div className="session-req">"{s.request}"</div>
            <div className="session-meta">{s.created_at?.slice(0,16)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function DecisionsPage({ decisions, projectPath, onAdd }: any) {
  const [title, setTitle]     = useState('');
  const [decision, setDec]    = useState('');
  const [reason, setReason]   = useState('');

  const submit = async () => {
    if (!title || !decision) return;
    await api.addDecision(projectPath, title, decision, reason, []).catch(() => {});
    setTitle(''); setDec(''); setReason('');
    onAdd();
  };

  return (
    <div className="page">
      <h1>Architectural Decisions</h1>
      <div className="decision-form">
        <input className="form-input" placeholder="Decision title" value={title} onChange={e=>setTitle(e.target.value)} />
        <textarea className="form-input" placeholder="Decision details" value={decision} onChange={e=>setDec(e.target.value)} rows={2} />
        <input className="form-input" placeholder="Reason (optional)" value={reason} onChange={e=>setReason(e.target.value)} />
        <button className="btn-action" onClick={submit}>Save Decision</button>
      </div>
      <div className="decision-list">
        {decisions.map((d: any) => (
          <div className="decision-row" key={d.id}>
            <div className="decision-title">{d.title}</div>
            <div className="decision-body">{d.decision}</div>
            {d.reason && <div className="decision-reason">Why: {d.reason}</div>}
            <div className="decision-date">{d.created_at?.slice(0,10)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function Analytics({ stats, savings, query, setQuery, runAsk, context, busy }: any) {
  return (
    <div className="page">
      <h1>AI Context & Analytics</h1>
      <div className="ask-bar">
        <input className="ask-input" placeholder="Ask about your codebase..."
          value={query} onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && runAsk()} />
        <button className="btn-ask" onClick={runAsk} disabled={busy}>
          {busy ? '...' : 'Get Context'}
        </button>
      </div>
      {savings && (
        <div className="savings-banner">
          <div className="sav-item"><div className="sav-val">{savings.original?.toLocaleString()}</div><div className="sav-label">Original tokens</div></div>
          <div className="sav-arrow">→</div>
          <div className="sav-item"><div className="sav-val green">{savings.optimized?.toLocaleString()}</div><div className="sav-label">Optimized tokens</div></div>
          <div className="sav-arrow">→</div>
          <div className="sav-item"><div className="sav-val accent">{savings.savings_pct}%</div><div className="sav-label">Savings</div></div>
        </div>
      )}
      {context && (
        <div className="context-box">
          <div className="context-hdr">Context Package <button className="btn-copy" onClick={() => navigator.clipboard.writeText(context)}>Copy</button></div>
          <pre className="context-body">{context}</pre>
        </div>
      )}
    </div>
  );
}

// ── Utils ─────────────────────────────────────────────────────────────────────
function cap(s: string) { return s[0].toUpperCase() + s.slice(1); }
function pageIcon(p: Page) {
  return { dashboard:'🏠', projects:'📁', memory:'🕸️', sessions:'📋', decisions:'💡', analytics:'⚡' }[p];
}
