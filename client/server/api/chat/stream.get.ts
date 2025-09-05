import { defineEventHandler, getQuery, sendStream } from 'h3'
import { subscribeToThread, unsubscribeFromThread } from '../../utils/chatEvents'

export default defineEventHandler(async (event) => {
  const { threadId } = getQuery(event)
  if (!threadId || typeof threadId !== 'string') {
    event.node.res.statusCode = 400
    return 'Missing threadId'
  }

  event.node.res.setHeader('Content-Type', 'text/event-stream')
  event.node.res.setHeader('Cache-Control', 'no-cache, no-transform')
  event.node.res.setHeader('Connection', 'keep-alive')
  event.node.res.flushHeaders?.()

  const write = (chunk: string) => {
    event.node.res.write(chunk)
  }
  const onClose = () => {
    unsubscribeFromThread(threadId, sub)
  }
  const sub = { write, onClose }
  subscribeToThread(threadId, sub)

  // ping to keep connection alive
  const ping = setInterval(() => write(`event: ping\n` + `data: {}\n\n`), 25000)

  event.node.req.on('close', () => {
    clearInterval(ping)
    onClose()
  })

  // initial comment
  write(': connected\n\n')

  return sendStream(event, event.node.res)
})


