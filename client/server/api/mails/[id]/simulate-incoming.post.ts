import { defineEventHandler, getRouterParam, readBody, createError } from 'h3';
import { appendMessageToThread, readMails } from '../../../utils/mails';

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id');
  const body = await readBody(event);
  const { text } = body || {};

  if (!id) throw createError({ statusCode: 400, statusMessage: 'Missing thread id' });
  if (!text) throw createError({ statusCode: 400, statusMessage: 'Text required' });

  const mails = await readMails();
  const thread = mails.find(m => String(m.id) === String(id));
  if (!thread) throw createError({ statusCode: 404, statusMessage: 'Thread not found' });

  const incoming = {
    id: `in-${Date.now()}`,
    from: thread.to?.email || 'user@example.com',
    to: thread.from?.email || 'noreply@example.com',
    text,
    date: new Date().toISOString(),
    isOutgoing: false,
    subject: `Re: ${thread.subject || ''}`
  };

  await appendMessageToThread(String(id), incoming);
  return { ok: true, message: incoming };
});


