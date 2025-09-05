import { defineEventHandler, readBody, createError } from 'h3'
import { readMails, writeMails } from '../../utils/mails'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const { subject, participantEmail, participantName } = body || {}

  const mails = await readMails()
  const id = `thread-${Date.now()}`

  const newThread = {
    id,
    subject: subject || participantName || participantEmail || 'New conversation',
    unread: false,
    from: { name: 'You', email: 'agent@noreply' },
    to: participantEmail ? { name: participantName || '', email: participantEmail } : undefined,
    preview: '',
    date: new Date().toISOString(),
    participants: ['agent@noreply'].concat(participantEmail ? [participantEmail] : []),
    messages: []
  }

  mails.push(newThread as any)
  await writeMails(mails)

  return { ok: true, thread: newThread }
})


