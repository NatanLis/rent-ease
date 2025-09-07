import { readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { defineEventHandler } from 'h3'

export default defineEventHandler(async () => {
  try {
    const path = join(process.cwd(), 'client', 'server', 'db', 'invoices.json')
    const raw = await readFile(path, 'utf-8').catch(async () => '[]')
    const list = JSON.parse(raw || '[]')
    return list
  } catch (e) {
    return []
  }
})


