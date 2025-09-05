// Simple in-memory SSE broadcaster per threadId
type Subscriber = {
  write: (chunk: string) => void
  onClose: () => void
}

const threadIdToSubscribers = new Map<string, Set<Subscriber>>()

export function subscribeToThread(threadId: string, subscriber: Subscriber) {
  if (!threadIdToSubscribers.has(threadId)) {
    threadIdToSubscribers.set(threadId, new Set())
  }
  threadIdToSubscribers.get(threadId)!.add(subscriber)
}

export function unsubscribeFromThread(threadId: string, subscriber: Subscriber) {
  const set = threadIdToSubscribers.get(threadId)
  if (!set) return
  set.delete(subscriber)
  if (set.size === 0) threadIdToSubscribers.delete(threadId)
}

export function publishToThread(threadId: string, event: string, payload: any) {
  const set = threadIdToSubscribers.get(threadId)
  if (!set || set.size === 0) return
  const data = `event: ${event}\n` + `data: ${JSON.stringify(payload)}\n\n`
  for (const sub of set) {
    try { sub.write(data) } catch (_) { /* ignore */ }
  }
}


