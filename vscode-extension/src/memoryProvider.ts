/**
 * memoryProvider.ts — TreeDataProviders for all 4 sidebar views.
 */
import * as vscode from 'vscode';
import * as path from 'path';
import { runCli } from './runner';

// ── Generic tree item ─────────────────────────────────────────────────────────

export class MemoryItem extends vscode.TreeItem {
  constructor(
    label: string,
    public readonly description_: string = '',
    collapsible = vscode.TreeItemCollapsibleState.None,
    public readonly contextValue_: string = '',
    iconId?: string,
  ) {
    super(label, collapsible);
    this.description = description_;
    this.contextValue = contextValue_;
    if (iconId) this.iconPath = new vscode.ThemeIcon(iconId);
  }
}

// ── Memory Explorer ───────────────────────────────────────────────────────────

export class MemoryExplorerProvider implements vscode.TreeDataProvider<MemoryItem> {
  private _onDidChange = new vscode.EventEmitter<MemoryItem | undefined>();
  readonly onDidChangeTreeData = this._onDidChange.event;

  private data: { files: number; functions: number; edges: number; decisions: number; sessions: number } | null = null;
  private files: string[] = [];

  constructor(private projectPath: string) {}

  refresh(projectPath?: string): void {
    if (projectPath) this.projectPath = projectPath;
    this.data = null;
    this.files = [];
    this._onDidChange.fire(undefined);
  }

  getTreeItem(el: MemoryItem) { return el; }

  async getChildren(el?: MemoryItem): Promise<MemoryItem[]> {
    if (!el) return this.getRoots();
    if (el.contextValue_ === 'filesGroup') return this.getFileItems();
    return [];
  }

  private async getRoots(): Promise<MemoryItem[]> {
    try {
      const raw = await runCli(['stats', '--json-compat'], this.projectPath).catch(() => '');
      // Parse stats from plain text output
      const parse = (label: string) => {
        const m = raw.match(new RegExp(label + '[^0-9]*(\\d+)'));
        return m ? m[1] : '—';
      };
      const items: MemoryItem[] = [
        new MemoryItem('Files indexed',    parse('Files indexed'),    vscode.TreeItemCollapsibleState.Collapsed, 'filesGroup',    'file-code'),
        new MemoryItem('Functions stored', parse('Functions stored'), vscode.TreeItemCollapsibleState.None,      '',              'symbol-method'),
        new MemoryItem('Graph edges',      parse('Graph edges'),      vscode.TreeItemCollapsibleState.None,      '',              'type-hierarchy'),
        new MemoryItem('Decisions',        parse('Decisions'),        vscode.TreeItemCollapsibleState.None,      '',              'checklist'),
        new MemoryItem('Sessions',         parse('Sessions'),         vscode.TreeItemCollapsibleState.None,      '',              'history'),
      ];
      return items;
    } catch {
      return [new MemoryItem('Not initialized', 'Run: Memory: Initialize Project', vscode.TreeItemCollapsibleState.None, '', 'warning')];
    }
  }

  private async getFileItems(): Promise<MemoryItem[]> {
    try {
      const raw = await runCli(['search', '.', '--limit', '20'], this.projectPath).catch(() => '');
      const lines = raw.split('\n').filter(l => l.includes('│') && !l.includes('File') && !l.includes('─'));
      return lines.map(l => {
        const parts = l.split('│').map(p => p.trim()).filter(Boolean);
        const name = parts[0] || '';
        const purpose = parts[1] || '';
        return new MemoryItem(name, purpose.substring(0, 60), vscode.TreeItemCollapsibleState.None, '', 'file');
      }).filter(i => i.label);
    } catch { return []; }
  }
}

// ── Graph Explorer ────────────────────────────────────────────────────────────

export class GraphExplorerProvider implements vscode.TreeDataProvider<MemoryItem> {
  private _onDidChange = new vscode.EventEmitter<MemoryItem | undefined>();
  readonly onDidChangeTreeData = this._onDidChange.event;

  constructor(private projectPath: string) {}

  refresh(projectPath?: string): void {
    if (projectPath) this.projectPath = projectPath;
    this._onDidChange.fire(undefined);
  }

  getTreeItem(el: MemoryItem) { return el; }

  async getChildren(): Promise<MemoryItem[]> {
    try {
      const raw = await runCli(['graph', this.projectPath], this.projectPath);
      const lines = raw.split('\n')
        .filter(l => l.includes('---->') || l.includes('--['))
        .slice(0, 30);
      return lines.map(l => {
        const clean = l.replace(/\x1b\[[0-9;]*m/g, '').trim();
        const [src, rest] = clean.split(/--\[.*?\]-->|---->/);
        return new MemoryItem(
          (src || '').trim(),
          '→ ' + (rest || '').trim(),
          vscode.TreeItemCollapsibleState.None,
          '',
          'arrow-right'
        );
      }).filter(i => i.label);
    } catch {
      return [new MemoryItem('No graph data', 'Run Memory: Index first', vscode.TreeItemCollapsibleState.None, '', 'info')];
    }
  }
}

// ── Token Savings ─────────────────────────────────────────────────────────────

export class TokenSavingsProvider implements vscode.TreeDataProvider<MemoryItem> {
  private _onDidChange = new vscode.EventEmitter<MemoryItem | undefined>();
  readonly onDidChangeTreeData = this._onDidChange.event;
  private lastQuery = '';
  private lastReport: { original: number; optimized: number; savings_pct: number } | null = null;

  constructor(private projectPath: string) {}

  refresh(projectPath?: string, query?: string, report?: any): void {
    if (projectPath) this.projectPath = projectPath;
    if (query) this.lastQuery = query;
    if (report) this.lastReport = report;
    this._onDidChange.fire(undefined);
  }

  getTreeItem(el: MemoryItem) { return el; }

  async getChildren(): Promise<MemoryItem[]> {
    if (!this.lastReport) {
      return [new MemoryItem('No query yet', 'Use Memory: Ask to see savings', vscode.TreeItemCollapsibleState.None, '', 'graph')];
    }
    const r = this.lastReport;
    return [
      new MemoryItem('Last query',       this.lastQuery.substring(0, 50),  vscode.TreeItemCollapsibleState.None, '', 'comment'),
      new MemoryItem('Original tokens',  `~${r.original.toLocaleString()}`, vscode.TreeItemCollapsibleState.None, '', 'arrow-up'),
      new MemoryItem('Optimized tokens', `${r.optimized.toLocaleString()}`, vscode.TreeItemCollapsibleState.None, '', 'arrow-down'),
      new MemoryItem('Savings',          `${r.savings_pct}%`,               vscode.TreeItemCollapsibleState.None, '', 'star'),
    ];
  }
}

// ── Session History ───────────────────────────────────────────────────────────

export class SessionHistoryProvider implements vscode.TreeDataProvider<MemoryItem> {
  private _onDidChange = new vscode.EventEmitter<MemoryItem | undefined>();
  readonly onDidChangeTreeData = this._onDidChange.event;
  private sessions: { request: string; created_at: string }[] = [];

  constructor(private projectPath: string) {}

  refresh(projectPath?: string): void {
    if (projectPath) this.projectPath = projectPath;
    this._onDidChange.fire(undefined);
  }

  addSession(request: string): void {
    this.sessions.unshift({ request, created_at: new Date().toLocaleTimeString() });
    if (this.sessions.length > 20) this.sessions.pop();
    this._onDidChange.fire(undefined);
  }

  getTreeItem(el: MemoryItem) { return el; }

  async getChildren(): Promise<MemoryItem[]> {
    if (!this.sessions.length) {
      return [new MemoryItem('No sessions yet', 'Sessions appear after Memory: Ask', vscode.TreeItemCollapsibleState.None, '', 'clock')];
    }
    return this.sessions.map(s =>
      new MemoryItem(
        s.request.substring(0, 50),
        s.created_at,
        vscode.TreeItemCollapsibleState.None,
        '',
        'comment-discussion'
      )
    );
  }
}
