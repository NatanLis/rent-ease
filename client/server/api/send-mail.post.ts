import { defineEventHandler, readBody, createError } from 'h3';
import { config as dotenvConfig } from 'dotenv';
import { resolve } from 'path';
import nodemailer from 'nodemailer';
import { appendMessageToThread } from '../utils/mails';
import type { Message } from '../../types/mail';

// Load env from client/.env and fallback to project root ../.env
dotenvConfig();
dotenvConfig({ path: resolve(process.cwd(), '..', '.env') });

// POST /api/send-mail
export default defineEventHandler(async (event) => {
  const body = await readBody(event);
  const { to, subject, text, html, mailId } = body || {};
  const fromEmail = process.env.MAIL_NOREPLY || process.env.SMTP_USER;
  const fromName = process.env.MAIL_FROM_NAME || 'NoReply';

  // Validate SMTP credentials early for clearer errors
  if (!process.env.SMTP_USER || !process.env.SMTP_PASS) {
    throw createError({
      statusCode: 500,
      statusMessage: 'SMTP credentials missing: set SMTP_USER and SMTP_PASS in .env'
    });
  }

  // Validate required fields
  if (!to || typeof to !== 'string') {
    throw createError({ statusCode: 400, statusMessage: 'Invalid recipient' });
  }
  if (!subject || typeof subject !== 'string') {
    throw createError({ statusCode: 400, statusMessage: 'Subject required' });
  }
  if (!text && !html) {
    throw createError({ statusCode: 400, statusMessage: 'Email body required' });
  }

  // Create Nodemailer transporter
  const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST || 'smtp.gmail.com',
    port: Number(process.env.SMTP_PORT) || 465,
    secure: (process.env.SMTP_PORT ? Number(process.env.SMTP_PORT) : 465) === 465, // true for 465, false for 587
    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASS
    }
  });

  // Verify SMTP connection
  try {
    await transporter.verify();
  } catch (err) {
    console.error('SMTP verification failed:', err);
    throw createError({
      statusCode: 500,
      statusMessage: `SMTP connection failed: ${(err as Error).message}`
    });
  }

  // Send email
  let info;
  try {
    info = await transporter.sendMail({
      from: `"${fromName}" <${fromEmail}>`,
      to,
      subject,
      text: text || undefined,
      html: html || undefined,
      replyTo: fromEmail,
      headers: {
        'X-Auto-Response-Suppress': 'All',
        'Auto-Submitted': 'auto-generated'
      }
    });
  } catch (err) {
    console.error('SMTP send failed:', err);
    throw createError({
      statusCode: 500,
      statusMessage: `Failed to send email: ${(err as Error).message}`
    });
  }

  // Append message to local DB / thread
  const msg: Message = {
    id: `msg-${Date.now()}-${Math.floor(Math.random() * 10000)}`,
    from: fromEmail || 'noreply',
    to,
    text: text || undefined,
    html: html || undefined,
    date: new Date().toISOString(),
    isOutgoing: true,
    subject
  };

  const threadId = mailId || `thread-${Date.now()}`;
  await appendMessageToThread(threadId, msg, {
    from: { name: 'You', email: fromEmail || '' },
    to: { name: '', email: to }
  });

  // Return success response
  return { ok: true, info, message: msg, mailId: threadId };
});
