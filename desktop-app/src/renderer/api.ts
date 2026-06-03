/** api.ts — All calls to the local FastAPI backend. */
const BASE = 'http://localhost:7842';

async function post(path: string, body: object) {
  const r = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

async function get(path: string, params?: Record<string, string>) {
  const url = new URL(`${BASE}${path}`);
  if (params) Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  const r = await fetch(url.toString());
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export const api = {
  health:     ()                         => get('/health'),
  init:       (project_path: string)    => post('/init',    { project_path }),
  index:      (project_path: string)    => post('/index',   { project_path }),
  update:     (project_path: string)    => post('/update',  { project_path }),
  ask:        (project_path: string, query: string, max_tokens = 3000) =>
                                           post('/ask', { project_path, query, max_tokens }),
  search:     (project_path: string, query: string) =>
                                           post('/search', { project_path, query, max_tokens: 3000 }),
  stats:      (project_path: string)    => get('/stats',    { project_path }),
  graph:      (project_path: string)    => get('/graph',    { project_path }),
  sessions:   (project_path: string)    => get('/sessions', { project_path }),
  decisions:  (project_path: string)    => get('/decisions',{ project_path }),
  addDecision:(project_path: string, title: string, decision: string, reason: string, tags: string[]) =>
                                           post('/decisions', { project_path, title, decision, reason, tags }),
  compress:   (project_path: string)    => post('/compress', { project_path }),
  projects:   ()                         => get('/projects'),
  addProject: (project_path: string)    => post('/projects/add', { project_path }),
};
