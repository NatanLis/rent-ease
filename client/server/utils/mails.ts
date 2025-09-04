// server/utils/mails.ts
import fs from 'fs/promises';
import { resolve } from 'path';
import type { Mail, Message } from '../../types/mail';

const DB_PATH = resolve(process.cwd(), 'server', 'db', 'mails.json');

export async function readMails(): Promise<Mail[]> {
  try {
    const raw = await fs.readFile(DB_PATH, 'utf-8');
    const data = JSON.parse(raw);
    return Array.isArray(data) ? data : [];
  } catch (err: any) {
    if (err && err.code === 'ENOENT') {
      await writeMails([]);
      return [];
    }
    throw err;
  }
}

export async function writeMails(mails: Mail[]) {
  await fs.mkdir(resolve(process.cwd(), 'server', 'db'), { recursive: true });
  await fs.writeFile(DB_PATH, JSON.stringify(mails, null, 2), 'utf-8');
}

export async function appendMessageToThread(mailId: string, msg: Message, threadSeed?: Partial<Mail>) {
  const mails = await readMails();
  const idx = mails.findIndex(m => m.id === mailId);

  if (idx === -1) {
    // Create a minimal new thread if missing
    const newThread: Mail = {
      id: mailId,
      subject: msg.subject || 'No subject',
      unread: false,
      from: threadSeed?.from || { name: 'You', email: process.env.SMTP_USER || '' },
      to:   threadSeed?.to   || { name: '',     email: msg.to },
      preview: msg.text?.slice(0, 120) || '',
      date: new Date().toISOString(),
      participants: Array.from(new Set([msg.from, msg.to].filter(Boolean))),
      messages: [msg]
    };
    mails.push(newThread);
  } else {
    mails[idx].messages.push(msg);
    mails[idx].unread = false;
    mails[idx].preview = msg.text?.slice(0, 120) || mails[idx].preview || '';
    mails[idx].date = new Date().toISOString();
    const p = new Set([...(mails[idx].participants || []), msg.from, msg.to].filter(Boolean));
    mails[idx].participants = Array.from(p);
  }

  await writeMails(mails);
  return msg;
}
