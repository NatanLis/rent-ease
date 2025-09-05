import { defineEventHandler, readBody, createError } from 'h3'
import { appendMessageToThread } from '../../utils/mails'
import { publishToThread } from '../../utils/chatEvents'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const { threadId, text, senderEmail, recipientEmail, subject } = body || {}

  if (!threadId) throw createError({ statusCode: 400, statusMessage: 'threadId required' })
  if (!text || typeof text !== 'string') throw createError({ statusCode: 400, statusMessage: 'text required' })

  const msg = {
    id: `msg-${Date.now()}-${Math.floor(Math.random() * 10000)}`,
    from: senderEmail || 'agent@noreply',
    to: recipientEmail || 'user@example.com',
    text,
    date: new Date().toISOString(),
    isOutgoing: true,
    subject: subject || ''
  }

  await appendMessageToThread(threadId, msg)
  publishToThread(threadId, 'message', msg)

  return { ok: true, message: msg }
})


