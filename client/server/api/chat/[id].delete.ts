import { defineEventHandler, getRouterParam, createError } from 'h3'
import { readMails, writeMails } from '../../utils/mails'

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  if (!id) {
    throw createError({ statusCode: 400, statusMessage: 'Missing thread id' })
  }

  const mails = await readMails()
  const idx = mails.findIndex(m => String(m.id) === String(id))
  if (idx === -1) {
    throw createError({ statusCode: 404, statusMessage: 'Thread not found' })
  }

  mails.splice(idx, 1)
  await writeMails(mails)
  
  return { ok: true }
})
