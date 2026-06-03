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
exports.runCli = runCli;
exports.runCliJson = runCliJson;
/**
 * runner.ts — Executes the Python CLI as a child process.
 * All communication between the extension and the memory engine goes through here.
 */
const cp = __importStar(require("child_process"));
const path = __importStar(require("path"));
const vscode = __importStar(require("vscode"));
function getConfig() {
    const cfg = vscode.workspace.getConfiguration('memoryEngine');
    return {
        python: cfg.get('pythonPath') || 'python',
        cliPath: cfg.get('cliPath') || '',
        maxTokens: cfg.get('maxTokens') || 3000,
    };
}
function resolveCli(cliPath) {
    if (cliPath)
        return cliPath;
    // Try to find cli/main.py relative to extension install dir
    const extDir = path.resolve(__dirname, '..', '..', 'memory-engine');
    return path.join(extDir, 'cli', 'main.py');
}
function runCli(args, projectPath, onData) {
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
        proc.stdout.on('data', (d) => {
            const text = d.toString();
            stdout += text;
            if (onData) {
                text.split('\n').filter(Boolean).forEach(onData);
            }
        });
        proc.stderr.on('data', (d) => { stderr += d.toString(); });
        proc.on('close', (code) => {
            if (code === 0) {
                resolve(stdout);
            }
            else {
                reject(new Error(stderr || `CLI exited with code ${code}`));
            }
        });
        proc.on('error', (err) => {
            reject(new Error(`Cannot start Python: ${err.message}\n` +
                `Check "memoryEngine.pythonPath" in settings.`));
        });
    });
}
/** Run CLI and return parsed JSON from last line */
async function runCliJson(args, projectPath) {
    const out = await runCli(args, projectPath);
    // Strip ANSI colour codes
    const clean = out.replace(/\x1b\[[0-9;]*m/g, '').trim();
    const lines = clean.split('\n').filter(Boolean);
    // Try last line as JSON
    try {
        return JSON.parse(lines[lines.length - 1]);
    }
    catch {
        return clean;
    }
}
//# sourceMappingURL=runner.js.map