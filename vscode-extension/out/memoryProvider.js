"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.SessionHistoryProvider = exports.TokenSavingsProvider = exports.GraphExplorerProvider = exports.MemoryExplorerProvider = exports.MemoryItem = void 0;
/**
 * memoryProvider.ts — TreeDataProviders for all 4 sidebar views.
 */
const vscode = __importStar(require("vscode"));
const runner_1 = require("./runner");
// ── Generic tree item ─────────────────────────────────────────────────────────
class MemoryItem extends vscode.TreeItem {
    constructor(label, description_ = '', collapsible = vscode.TreeItemCollapsibleState.None, contextValue_ = '', iconId) {
        super(label, collapsible);
        this.description_ = description_;
        this.contextValue_ = contextValue_;
        this.description = description_;
        this.contextValue = contextValue_;
        if (iconId)
            this.iconPath = new vscode.ThemeIcon(iconId);
    }
}
exports.MemoryItem = MemoryItem;
// ── Memory Explorer ───────────────────────────────────────────────────────────
class MemoryExplorerProvider {
    constructor(projectPath) {
        this.projectPath = projectPath;
        this._onDidChange = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChange.event;
        this.data = null;
        this.files = [];
    }
    refresh(projectPath) {
        if (projectPath)
            this.projectPath = projectPath;
        this.data = null;
        this.files = [];
        this._onDidChange.fire(undefined);
    }
    getTreeItem(el) { return el; }
    async getChildren(el) {
        if (!el)
            return this.getRoots();
        if (el.contextValue_ === 'filesGroup')
            return this.getFileItems();
        return [];
    }
    async getRoots() {
        try {
            const raw = await (0, runner_1.runCli)(['stats', '--json-compat'], this.projectPath).catch(() => '');
            // Parse stats from plain text output
            const parse = (label) => {
                const m = raw.match(new RegExp(label + '[^0-9]*(\\d+)'));
                return m ? m[1] : '—';
            };
            const items = [
                new MemoryItem('Files indexed', parse('Files indexed'), vscode.TreeItemCollapsibleState.Collapsed, 'filesGroup', 'file-code'),
                new MemoryItem('Functions stored', parse('Functions stored'), vscode.TreeItemCollapsibleState.None, '', 'symbol-method'),
                new MemoryItem('Graph edges', parse('Graph edges'), vscode.TreeItemCollapsibleState.None, '', 'type-hierarchy'),
                new MemoryItem('Decisions', parse('Decisions'), vscode.TreeItemCollapsibleState.None, '', 'checklist'),
                new MemoryItem('Sessions', parse('Sessions'), vscode.TreeItemCollapsibleState.None, '', 'history'),
            ];
            return items;
        }
        catch {
            return [new MemoryItem('Not initialized', 'Run: Memory: Initialize Project', vscode.TreeItemCollapsibleState.None, '', 'warning')];
        }
    }
    async getFileItems() {
        try {
            const raw = await (0, runner_1.runCli)(['search', '.', '--limit', '20'], this.projectPath).catch(() => '');
            const lines = raw.split('\n').filter(l => l.includes('│') && !l.includes('File') && !l.includes('─'));
            return lines.map(l => {
                const parts = l.split('│').map(p => p.trim()).filter(Boolean);
                const name = parts[0] || '';
                const purpose = parts[1] || '';
                return new MemoryItem(name, purpose.substring(0, 60), vscode.TreeItemCollapsibleState.None, '', 'file');
            }).filter(i => i.label);
        }
        catch {
            return [];
        }
    }
}
exports.MemoryExplorerProvider = MemoryExplorerProvider;
// ── Graph Explorer ────────────────────────────────────────────────────────────
class GraphExplorerProvider {
    constructor(projectPath) {
        this.projectPath = projectPath;
        this._onDidChange = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChange.event;
    }
    refresh(projectPath) {
        if (projectPath)
            this.projectPath = projectPath;
        this._onDidChange.fire(undefined);
    }
    getTreeItem(el) { return el; }
    async getChildren() {
        try {
            const raw = await (0, runner_1.runCli)(['graph', this.projectPath], this.projectPath);
            const lines = raw.split('\n')
                .filter(l => l.includes('---->') || l.includes('--['))
                .slice(0, 30);
            return lines.map(l => {
                const clean = l.replace(/\x1b\[[0-9;]*m/g, '').trim();
                const [src, rest] = clean.split(/--\[.*?\]-->|---->/);
                return new MemoryItem((src || '').trim(), '→ ' + (rest || '').trim(), vscode.TreeItemCollapsibleState.None, '', 'arrow-right');
            }).filter(i => i.label);
        }
        catch {
            return [new MemoryItem('No graph data', 'Run Memory: Index first', vscode.TreeItemCollapsibleState.None, '', 'info')];
        }
    }
}
exports.GraphExplorerProvider = GraphExplorerProvider;
// ── Token Savings ─────────────────────────────────────────────────────────────
class TokenSavingsProvider {
    constructor(projectPath) {
        this.projectPath = projectPath;
        this._onDidChange = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChange.event;
        this.lastQuery = '';
        this.lastReport = null;
    }
    refresh(projectPath, query, report) {
        if (projectPath)
            this.projectPath = projectPath;
        if (query)
            this.lastQuery = query;
        if (report)
            this.lastReport = report;
        this._onDidChange.fire(undefined);
    }
    getTreeItem(el) { return el; }
    async getChildren() {
        if (!this.lastReport) {
            return [new MemoryItem('No query yet', 'Use Memory: Ask to see savings', vscode.TreeItemCollapsibleState.None, '', 'graph')];
        }
        const r = this.lastReport;
        return [
            new MemoryItem('Last query', this.lastQuery.substring(0, 50), vscode.TreeItemCollapsibleState.None, '', 'comment'),
            new MemoryItem('Original tokens', `~${r.original.toLocaleString()}`, vscode.TreeItemCollapsibleState.None, '', 'arrow-up'),
            new MemoryItem('Optimized tokens', `${r.optimized.toLocaleString()}`, vscode.TreeItemCollapsibleState.None, '', 'arrow-down'),
            new MemoryItem('Savings', `${r.savings_pct}%`, vscode.TreeItemCollapsibleState.None, '', 'star'),
        ];
    }
}
exports.TokenSavingsProvider = TokenSavingsProvider;
// ── Session History ───────────────────────────────────────────────────────────
class SessionHistoryProvider {
    constructor(projectPath) {
        this.projectPath = projectPath;
        this._onDidChange = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChange.event;
        this.sessions = [];
    }
    refresh(projectPath) {
        if (projectPath)
            this.projectPath = projectPath;
        this._onDidChange.fire(undefined);
    }
    addSession(request) {
        this.sessions.unshift({ request, created_at: new Date().toLocaleTimeString() });
        if (this.sessions.length > 20)
            this.sessions.pop();
        this._onDidChange.fire(undefined);
    }
    getTreeItem(el) { return el; }
    async getChildren() {
        if (!this.sessions.length) {
            return [new MemoryItem('No sessions yet', 'Sessions appear after Memory: Ask', vscode.TreeItemCollapsibleState.None, '', 'clock')];
        }
        return this.sessions.map(s => new MemoryItem(s.request.substring(0, 50), s.created_at, vscode.TreeItemCollapsibleState.None, '', 'comment-discussion'));
    }
}
exports.SessionHistoryProvider = SessionHistoryProvider;
//# sourceMappingURL=memoryProvider.js.map