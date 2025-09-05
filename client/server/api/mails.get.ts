// server/api/mails.get.ts
import { defineEventHandler } from 'h3';
import { readMails } from '../utils/mails';

export default defineEventHandler(async () => {
  try {
    const mails = await readMails();
    return mails;
  } catch (err) {
    console.error('Failed to load mails:', err);
    // Return an empty list instead of failing the request
    return [];
  }
});