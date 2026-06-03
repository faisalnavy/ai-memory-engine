/** Landing page — hero, features, pricing, CTA */
import Link from 'next/link';

export default function Home() {
  return (
    <main style={{ background: '#0f1117', minHeight: '100vh', color: '#e2e8f0', fontFamily: 'system-ui' }}>

      {/* Nav */}
      <nav style={{ display:'flex', justifyContent:'space-between', alignItems:'center',
                    padding:'18px 60px', borderBottom:'1px solid #1e2130' }}>
        <span style={{ fontSize:20, fontWeight:700, color:'#a78bfa' }}>🧠 AI Memory Engine</span>
        <div style={{ display:'flex', gap:24, alignItems:'center' }}>
          <Link href="#features" style={{ color:'#94a3b8', textDecoration:'none' }}>Features</Link>
          <Link href="#pricing"  style={{ color:'#94a3b8', textDecoration:'none' }}>Pricing</Link>
          <Link href="/login"    style={{ color:'#94a3b8', textDecoration:'none' }}>Login</Link>
          <Link href="/register" style={{ background:'#6c63ff', color:'white', padding:'8px 20px',
                                          borderRadius:8, textDecoration:'none', fontWeight:600 }}>
            Get Started Free
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section style={{ textAlign:'center', padding:'100px 20px 80px' }}>
        <div style={{ display:'inline-block', background:'#6c63ff22', color:'#a78bfa',
                      padding:'6px 16px', borderRadius:20, fontSize:13, marginBottom:24 }}>
          🚀 Open Source · Works with Claude, Cursor, Copilot, GPT-4
        </div>
        <h1 style={{ fontSize:56, fontWeight:800, lineHeight:1.1, marginBottom:24,
                     background:'linear-gradient(135deg, #a78bfa, #6c63ff)',
                     WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent' }}>
          Reduce AI Token Usage<br/>by 90–98%
        </h1>
        <p style={{ fontSize:20, color:'#94a3b8', maxWidth:600, margin:'0 auto 40px' }}>
          Smart project memory that makes your AI coding assistant 10x cheaper and more accurate.
          Index once, save forever.
        </p>
        <div style={{ display:'flex', gap:16, justifyContent:'center' }}>
          <Link href="/register" style={{ background:'#6c63ff', color:'white', padding:'14px 32px',
                                          borderRadius:10, textDecoration:'none', fontWeight:700, fontSize:16 }}>
            Start for Free
          </Link>
          <Link href="https://github.com/faisalnavy/ai-memory-engine"
                style={{ background:'#1a1d27', color:'#e2e8f0', padding:'14px 32px',
                         borderRadius:10, textDecoration:'none', fontWeight:600, fontSize:16 }}>
            ⭐ GitHub
          </Link>
        </div>

        {/* Token savings demo */}
        <div style={{ display:'flex', gap:32, justifyContent:'center', marginTop:60 }}>
          {[['52,000','Without Memory','#ef444422','#ef4444'],
            ['890',   'With Memory Engine','#22c55e22','#22c55e'],
            ['98.3%', 'Token Savings','#6c63ff22','#a78bfa']].map(([val,label,bg,color]) => (
            <div key={label} style={{ background:bg, border:`1px solid ${color}33`,
                                      padding:'20px 32px', borderRadius:12, textAlign:'center' }}>
              <div style={{ fontSize:36, fontWeight:800, color }}>{val}</div>
              <div style={{ color:'#64748b', fontSize:13, marginTop:4 }}>{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section id="features" style={{ padding:'80px 60px', maxWidth:1100, margin:'0 auto' }}>
        <h2 style={{ textAlign:'center', fontSize:36, fontWeight:700, marginBottom:48, color:'#e2e8f0' }}>
          Everything you need
        </h2>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:24 }}>
          {FEATURES.map(f => (
            <div key={f.title} style={{ background:'#1a1d27', borderRadius:14, padding:'28px 24px' }}>
              <div style={{ fontSize:32, marginBottom:14 }}>{f.icon}</div>
              <h3 style={{ color:'#a78bfa', fontSize:17, fontWeight:600, marginBottom:10 }}>{f.title}</h3>
              <p style={{ color:'#64748b', fontSize:14, lineHeight:1.6 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" style={{ padding:'80px 60px', maxWidth:1100, margin:'0 auto' }}>
        <h2 style={{ textAlign:'center', fontSize:36, fontWeight:700, marginBottom:48, color:'#e2e8f0' }}>
          Simple, honest pricing
        </h2>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:20 }}>
          {PLANS.map(p => (
            <div key={p.name} style={{ background: p.highlight ? '#6c63ff' : '#1a1d27',
                                        borderRadius:14, padding:'28px 22px',
                                        border: p.highlight ? 'none' : '1px solid #1e2130' }}>
              <div style={{ fontSize:14, color: p.highlight ? '#d4d0ff' : '#64748b', marginBottom:8 }}>{p.name}</div>
              <div style={{ fontSize:36, fontWeight:800, color:'white', marginBottom:4 }}>{p.price}</div>
              <div style={{ fontSize:12, color: p.highlight ? '#d4d0ff' : '#64748b', marginBottom:24 }}>/month</div>
              {p.features.map(f => (
                <div key={f} style={{ display:'flex', gap:8, marginBottom:10, fontSize:13,
                                       color: p.highlight ? '#e2e8f0' : '#94a3b8' }}>
                  <span style={{ color: p.highlight ? '#fff' : '#22c55e' }}>✓</span> {f}
                </div>
              ))}
              <Link href="/register" style={{ display:'block', textAlign:'center', marginTop:24,
                                              background: p.highlight ? 'white' : '#6c63ff',
                                              color: p.highlight ? '#6c63ff' : 'white',
                                              padding:'10px 0', borderRadius:8,
                                              textDecoration:'none', fontWeight:600 }}>
                {p.cta}
              </Link>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer style={{ borderTop:'1px solid #1e2130', padding:'40px 60px',
                        display:'flex', justifyContent:'space-between', alignItems:'center' }}>
        <span style={{ color:'#64748b', fontSize:13 }}>© 2026 AI Memory Engine · MIT License</span>
        <div style={{ display:'flex', gap:24 }}>
          <Link href="https://github.com/faisalnavy/ai-memory-engine" style={{ color:'#64748b', fontSize:13, textDecoration:'none' }}>GitHub</Link>
          <Link href="/api/docs" style={{ color:'#64748b', fontSize:13, textDecoration:'none' }}>API Docs</Link>
        </div>
      </footer>
    </main>
  );
}

const FEATURES = [
  { icon:'🗂️', title:'7-Layer Memory',       desc:'Project DNA, files, functions, dependency graph, sessions, decisions — all compressed and instantly searchable.' },
  { icon:'⚡', title:'Incremental Updates',  desc:'Hash-based diffing means only changed files are re-indexed. Stays fast on projects with 5000+ files.' },
  { icon:'🕸️', title:'Knowledge Graph',      desc:'NetworkX dependency graph maps every import, call, and inheritance. Context is graph-aware, not just keyword-matched.' },
  { icon:'🌐', title:'Works with Any AI',    desc:'Claude, Cursor, Copilot, GPT-4, Gemini, Windsurf — paste context anywhere. No vendor lock-in.' },
  { icon:'👥', title:'Team Collaboration',   desc:'Share memory databases across your team. Everyone gets the same high-quality context for the same project.' },
  { icon:'📊', title:'Analytics Dashboard',  desc:'Track exactly how many tokens you saved, per project, per month. See your ROI in real time.' },
];

const PLANS = [
  { name:'Free',       price:'$0',   highlight:false, cta:'Get Started',  features:['3 projects','CLI + GUI app','Community support','Local storage only'] },
  { name:'Pro',        price:'$12',  highlight:true,  cta:'Start Pro',    features:['20 projects','API access','Priority support','Cloud sync'] },
  { name:'Team',       price:'$49',  highlight:false, cta:'Start Team',   features:['100 projects','10 team members','Webhooks + SDK','Analytics'] },
  { name:'Enterprise', price:'Custom',highlight:false, cta:'Contact Us',  features:['Unlimited projects','SSO/SAML','Dedicated support','SLA guarantee'] },
];
