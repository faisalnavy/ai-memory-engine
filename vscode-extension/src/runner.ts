/**
 * runner.ts — Executes the Python CLI as a child process.
 * All communication between the extension and the memory engine goes through here.
 */
import * as cp from 'child_process';
import * as path from 'path';
import * as vscode from 'vscode';

function getConfig() {
  const cfg = vscode.workspace.getConfiguration('memoryEngine');
  return {
    python:   cfg.get<string>('pythonPath') || 'python',
    cliPath:  cfg.get<string>('cliPath')    || '',
    maxTokens: cfg.get<number>('maxTokens') || 3000,
  };
}

function resolveCli(cliPath: string): string {
  if (cliPath) return cliPath;
  // Try to find cli/main.py relative to extension install dir
  const extDir = path.resolve(__dirname, '..', '..', 'memory-engine');
  return path.join(extDir, 'cli', 'main.py');
}

export function runCli(
  args: string[],
  projectPath: string,
  onData?: (line: string) => void
): Promise<string> {
  return new Promise((resolve, reject) => {
    const { python, cliPath } = getConfig();
    const cli = resolveCli(cliPath);

    const fullArgs = ['-X', 'utf8', cli, ...args, projectPath];
    const proc = cp.spawn(python, fullArgs, {
      cwd: projectPath,
      env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
    });

    let stdout = '';
    let stderr = '';

    proc.stdout.on('data', (d: Buffer) => {
      const text = d.toString();
      stdout += text;
      if (onData) {
        text.split('\n').filter(Boolean).forEach(onData);
      }
    });

    proc.stderr.on('data', (d: Buffer) => { stderr += d.toString(); });

    proc.on('close', (code) => {
      if (code === 0) {
        resolve(stdout);
      } else {
        reject(new Error(stderr || `CLI exited with code ${code}`));
      }
    });

    proc.on('error', (err) => {
      reject(new Error(
        `Cannot start Python: ${err.message}\n` +
        `Check "memoryEngine.pythonPath" in settings.`
      ));
    });
  });
}

/** Run CLI and return parsed JSON from last line */
export async function runCliJson(
  args: string[],
  projectPath: string
): Promise<any> {
  const out = await runCli(args, projectPath);
  // Strip ANSI colour codes
  const clean = out.replace(/\x1b\[[0-9;]*m/g, '').trim();
  const lines = clean.split('\n').filter(Boolean);
  // Try last line as JSON
  try { return JSON.parse(lines[lines.length - 1]); } catch { return clean; }
}
