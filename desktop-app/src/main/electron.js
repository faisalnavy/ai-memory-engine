/**
 * electron.js — Electron main process.
 * Starts the Python FastAPI backend, then opens the React window.
 */
const { app, BrowserWindow, Tray, Menu, ipcMain, shell, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;
const API_PORT = 7842;
let mainWindow = null;
let tray = null;
let apiProcess = null;

// ── Start Python FastAPI backend ─────────────────────────────────────────────

function startApi() {
  let apiExe, apiArgs;

  if (isDev) {
    // Development: run via python
    const python = process.platform === 'win32' ? 'python' : 'python3';
    const apiPath = path.join(__dirname, '..', '..', 'api', 'server.py');
    apiExe  = python;
    apiArgs = ['-X', 'utf8', apiPath, '--port', String(API_PORT)];
  } else {
    // Production: use bundled api.exe (Windows) or api binary (Mac/Linux)
    const exeName = process.platform === 'win32' ? 'api.exe' : 'api';
    apiExe  = path.join(process.resourcesPath, 'api-dist', exeName);
    apiArgs = ['--port', String(API_PORT)];
  }

  apiProcess = spawn(apiExe, apiArgs, {
    env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
  });

  apiProcess.stdout.on('data', d => console.log('[API]', d.toString()));
  apiProcess.stderr.on('data', d => console.error('[API ERR]', d.toString()));
  apiProcess.on('close', code => console.log('[API] exited', code));
}

function waitForApi(retries = 20) {
  return new Promise((resolve, reject) => {
    const attempt = (n) => {
      http.get(`http://localhost:${API_PORT}/health`, (res) => {
        if (res.statusCode === 200) resolve();
        else if (n > 0) setTimeout(() => attempt(n - 1), 500);
        else reject(new Error('API did not start'));
      }).on('error', () => {
        if (n > 0) setTimeout(() => attempt(n - 1), 500);
        else reject(new Error('API did not start'));
      });
    };
    attempt(retries);
  });
}

// ── Create main window ────────────────────────────────────────────────────────

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    title: 'AI Memory Engine',
    backgroundColor: '#0f1117',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    show: false,
  });

  const url = isDev ? 'http://localhost:5173' : `file://${path.join(__dirname, '../../dist/index.html')}`;
  mainWindow.loadURL(url);

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    if (isDev) mainWindow.webContents.openDevTools();
  });

  mainWindow.on('close', (e) => {
    if (!app.isQuitting) {
      e.preventDefault();
      mainWindow.hide();
    }
  });
}

// ── System tray ───────────────────────────────────────────────────────────────

function createTray() {
  const iconPath = path.join(__dirname, '../../public/tray-icon.png');
  try {
    tray = new Tray(iconPath);
  } catch {
    // icon not found — skip tray
    return;
  }

  const menu = Menu.buildFromTemplate([
    { label: 'Open AI Memory Engine', click: () => { mainWindow?.show(); mainWindow?.focus(); } },
    { type: 'separator' },
    { label: 'Quit', click: () => { app.isQuitting = true; app.quit(); } },
  ]);

  tray.setToolTip('AI Memory Engine');
  tray.setContextMenu(menu);
  tray.on('double-click', () => { mainWindow?.show(); mainWindow?.focus(); });
}

// ── IPC handlers ──────────────────────────────────────────────────────────────

ipcMain.handle('select-folder', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory'],
    title: 'Select Project Folder',
  });
  return result.canceled ? null : result.filePaths[0];
});

ipcMain.handle('open-external', async (_, url) => {
  shell.openExternal(url);
});

ipcMain.handle('get-api-port', () => API_PORT);

// ── App lifecycle ─────────────────────────────────────────────────────────────

app.whenReady().then(async () => {
  startApi();
  try {
    await waitForApi();
    console.log('[Electron] API ready on port', API_PORT);
  } catch (e) {
    console.error('[Electron] API failed to start:', e.message);
  }
  createWindow();
  createTray();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (!mainWindow) createWindow();
  else mainWindow.show();
});

app.on('before-quit', () => {
  app.isQuitting = true;
  if (apiProcess) apiProcess.kill();
});
