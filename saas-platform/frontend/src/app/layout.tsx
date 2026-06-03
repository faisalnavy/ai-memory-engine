import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'AI Memory Engine — Reduce AI Token Usage by 90-98%',
  description: 'Smart project memory for AI coding assistants. Works with Claude, Cursor, Copilot, GPT-4.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin:0, padding:0, background:'#0f1117' }}>{children}</body>
    </html>
  );
}
