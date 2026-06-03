/**
 * extension.ts — Main VS Code extension entry point.
 * Registers all commands, views, status bar, and file watcher.
 */
import * as vscode from 'vscode';
import * as path from 'path';
import { runCli } from './runner';
import {
  MemoryExplorerProvider,
  GraphExplorerProvider,
  TokenSavingsProvider,
  SessionHistoryProvider,
} from './memoryProvider';

// ── State ─────────────────────────────────────────────────────────────────────

let statusBar: vscode.StatusBarItem;
let fileWatcher: vscode.FileSystemWatcher | undefined;
let memoryProvider: MemoryExplorerProvider;
let graphProvider: GraphExplorerProvider;
let savingsProvider: TokenSavingsProvider;
let sessionProvider: SessionHistoryProvider;

// ── Activation ────────────────────────────────────────────────────────────────

export function activate(ctx: vscode.ExtensionContext) {
  const projectPath = getProjectPath();

  // Status bar
  statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
  statusBar.command = 'memoryEngine.stats';
  updateStatusBar('🧠 Memory', 'idle');
  statusBar.show();
  ctx.subscriptions.push(statusBar);

  // Tree providers
  memoryProvider = new MemoryExplorerProvider(projectPath);
  graphProvider  = new GraphExplorerProvider(projectPath);
  savingsProvider = new TokenSavingsProvider(projectPath);
  sessionProvider = new SessionHistoryProvider(projectPath);

  ctx.subscriptions.push(
    vscode.window.registerTreeDataProvider('memoryExplorer', memoryProvider),
    vscode.window.registerTreeDataProvider('graphExplorer',  graphProvider),
    vscode.window.registerTreeDataProvider('tokenSavings',   savingsProvider),
    vscode.window.registerTreeDataProvider('sessionHistory', sessionProvider),
  );

  // Register all commands
  ctx.subscriptions.push(
    vscode.commands.registerCommand('memoryEngine.init',     cmdInit),
    vscode.commands.registerCommand('memoryEngine.index',    cmdIndex),
    vscode.commands.registerCommand('memoryEngine.update',   cmdUpdate),
    vscode.commands.registerCommand('memoryEngine.ask',      cmdAsk),
    vscode.commands.registerCommand('memoryEngine.search',   cmdSearch),
    vscode.commands.registerCommand('memoryEngine.stats',    cmdStats),
    vscode.commands.registerCommand('memoryEngine.compress', cmdCompress),
    vscode.commands.registerCommand('memoryEngine.refresh',  cmdRefresh),
  );

  // File watcher — auto-update on save
  startFileWatcher(projectPath);

  // Auto-refresh views
  refreshAll(projectPath);

  vscode.window.showInformationMessage('🧠 AI Memory Engine is active!');
}

export function deactivate() {
  fileWatcher?.dispose();
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function getProjectPath(): string {
  return vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '';
}

function updateStatusBar(text: string, state: 'idle' | 'busy' | 'ok' | 'error') {
  const colors: Record<string, string> = {
    idle: '',
    busy: 'statusBarItem.warningBackground',
    ok:   'statusBarItem.prominentBackground',
    error:'statusBarItem.errorBackground',
  };
  statusBar.text = text;
  statusBar.backgroundColor = colors[state]
    ? new vscode.ThemeColor(colors[state])
    : undefined;
}

function refreshAll(projectPath?: string) {
  const p = projectPath || getProjectPath();
  memoryProvider.refresh(p);
  graphProvider.refresh(p);
  sessionProvider.refresh(p);
}

function startFileWatcher(projectPath: string) {
  fileWatcher?.dispose();
  const cfg = vscode.workspace.getConfiguration('memoryEngine');
  if (!cfg.get<boolean>('autoUpdate')) return;

  const pattern = new vscode.RelativePattern(
    projectPath,
    '**/*.{py,js,ts,jsx,tsx,go,rs,java,cs}'
  );

  fileWatcher = vscode.workspace.createFileSystemWatcher(pattern);
  fileWatcher.onDidChange(async (uri) => {
    // Skip .memory/ folder
    if (uri.fsPath.includes('.memory')) return;
    updateStatusBar('🧠 Updating...', 'busy');
    try {
      await runCli(['update'], projectPath);
      updateStatusBar('🧠 Memory ✓', 'ok');
      memoryProvider.refresh();
    } catch {
      updateStatusBar('🧠 Memory', 'idle');
    }
    // Reset to idle after 3s
    setTimeout(() => updateStatusBar('🧠 Memory', 'idle'), 3000);
  });
}

// ── Commands ──────────────────────────────────────────────────────────────────

async function cmdInit() {
  const projectPath = getProjectPath();
  if (!projectPath) {
    vscode.window.showErrorMessage('Open a folder first.');
    return;
  }

  await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: 'Memory: Initializing...', cancellable: false },
    async (progress) => {
      try {
        progress.report({ message: 'Creating .memory/ database...' });
        const out = await runCli(['init'], projectPath);
        progress.report({ message: 'Done!' });
        vscode.window.showInformationMessage('🧠 Memory initialized! Now run Memory: Index.');
        refreshAll(projectPath);
      } catch (e: any) {
        vscode.window.showErrorMessage('Init failed: ' + e.message);
      }
    }
  );
}

async function cmdIndex() {
  const projectPath = getProjectPath();
  if (!projectPath) { vscode.window.showErrorMessage('Open a folder first.'); return; }

  const panel = vscode.window.createOutputChannel('Memory Engine');
  panel.show(true);
  panel.appendLine('🧠 Indexing project...\n');
  updateStatusBar('🧠 Indexing...', 'busy');

  try {
    await runCli(['index'], projectPath, (line) => {
      const clean = line.replace(/\x1b\[[0-9;]*m/g, '');
      panel.appendLine(clean);
    });
    updateStatusBar('🧠 Memory ✓', 'ok');
    panel.appendLine('\n✅ Indexing complete!');
    vscode.window.showInformationMessage('🧠 Memory indexed! Use Memory: Ask to get AI context.');
    refreshAll(projectPath);
    startFileWatcher(projectPath);
  } catch (e: any) {
    updateStatusBar('🧠 Error', 'error');
    panel.appendLine('\n❌ Error: ' + e.message);
    vscode.window.showErrorMessage('Index failed: ' + e.message);
  }

  setTimeout(() => updateStatusBar('🧠 Memory', 'idle'), 4000);
}

async function cmdUpdate() {
  const projectPath = getProjectPath();
  updateStatusBar('🧠 Updating...', 'busy');
  try {
    const out = await runCli(['update'], projectPath);
    const clean = out.replace(/\x1b\[[0-9;]*m/g, '');
    if (clean.includes('up to date')) {
      vscode.window.showInformationMessage('🧠 Memory: Everything up to date.');
    } else {
      vscode.window.showInformationMessage('🧠 Memory updated! ' + clean.split('\n')[0]);
    }
    updateStatusBar('🧠 Memory ✓', 'ok');
    refreshAll(projectPath);
  } catch (e: any) {
    updateStatusBar('🧠 Error', 'error');
    vscode.window.showErrorMessage('Update failed: ' + e.message);
  }
  setTimeout(() => updateStatusBar('🧠 Memory', 'idle'), 3000);
}

async function cmdAsk() {
  const projectPath = getProjectPath();
  if (!projectPath) { vscode.window.showErrorMessage('Open a folder first.'); return; }

  const query = await vscode.window.showInputBox({
    prompt: 'What do you want to ask about your codebase?',
    placeHolder: 'e.g. how does user authentication work',
  });
  if (!query) return;

  updateStatusBar('🧠 Retrieving...', 'busy');
  const panel = vscode.window.createOutputChannel('Memory: Context Package');
  panel.show(true);
  panel.appendLine(`Query: "${query}"\n${'─'.repeat(60)}`);

  try {
    const cfg = vscode.workspace.getConfiguration('memoryEngine');
    const maxTokens = cfg.get<number>('maxTokens') || 3000;

    await runCli(['ask', query, '--max-tokens', String(maxTokens)], projectPath, (line) => {
      const clean = line.replace(/\x1b\[[0-9;]*m/g, '');
      panel.appendLine(clean);
    });

    // Parse savings from output for the sidebar
    const raw = await runCli(['ask', query, '--no-context', '--max-tokens', String(maxTokens)], projectPath).catch(() => '');
    const origMatch  = raw.match(/Original context.*?(\d[\d,]+)/);
    const optMatch   = raw.match(/Optimized context.*?(\d[\d,]+)/);
    const savingMatch= raw.match(/Token savings.*?([\d.]+)%/);
    if (origMatch && optMatch && savingMatch) {
      savingsProvider.refresh(projectPath, query, {
        original:    parseInt(origMatch[1].replace(',', '')),
        optimized:   parseInt(optMatch[1].replace(',', '')),
        savings_pct: parseFloat(savingMatch[1]),
      });
    }

    sessionProvider.addSession(query);
    updateStatusBar('🧠 Memory ✓', 'ok');

    // Copy to clipboard option
    const action = await vscode.window.showInformationMessage(
      `🧠 Context ready! Copy to clipboard to paste into your AI?`,
      'Copy Context', 'Dismiss'
    );
    if (action === 'Copy Context') {
      const ctx = panel.name;
      vscode.env.clipboard.writeText(raw);
      vscode.window.showInformationMessage('Context copied to clipboard!');
    }
  } catch (e: any) {
    updateStatusBar('🧠 Error', 'error');
    panel.appendLine('\n❌ Error: ' + e.message);
    vscode.window.showErrorMessage('Ask failed: ' + e.message);
  }
  setTimeout(() => updateStatusBar('🧠 Memory', 'idle'), 3000);
}

async function cmdSearch() {
  const projectPath = getProjectPath();
  const query = await vscode.window.showInputBox({
    prompt: 'Search memory — files and functions',
    placeHolder: 'e.g. authentication, database, user',
  });
  if (!query) return;

  const panel = vscode.window.createOutputChannel('Memory: Search Results');
  panel.show(true);
  try {
    await runCli(['search', query], projectPath, (line) => {
      panel.appendLine(line.replace(/\x1b\[[0-9;]*m/g, ''));
    });
  } catch (e: any) {
    vscode.window.showErrorMessage('Search failed: ' + e.message);
  }
}

async function cmdStats() {
  const projectPath = getProjectPath();
  const panel = vscode.window.createOutputChannel('Memory: Stats');
  panel.show(true);
  try {
    await runCli(['stats'], projectPath, (line) => {
      panel.appendLine(line.replace(/\x1b\[[0-9;]*m/g, ''));
    });
  } catch (e: any) {
    vscode.window.showErrorMessage('Stats failed: ' + e.message);
  }
}

async function cmdCompress() {
  const projectPath = getProjectPath();
  try {
    await vscode.window.withProgress(
      { location: vscode.ProgressLocation.Notification, title: 'Compressing sessions...', cancellable: false },
      async () => {
        await runCli(['compress', '--force'], projectPath);
      }
    );
    vscode.window.showInformationMessage('🧠 Sessions compressed into intelligence block.');
  } catch (e: any) {
    vscode.window.showErrorMessage('Compress failed: ' + e.message);
  }
}

async function cmdRefresh() {
  refreshAll();
  vscode.window.showInformationMessage('🧠 Memory views refreshed.');
}
