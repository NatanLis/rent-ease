import { readFile, writeFile, mkdir } from 'node:fs/promises'
import { join } from 'node:path'
import { defineEventHandler, readMultipartFormData, createError } from 'h3'

export default defineEventHandler(async (event) => {
  const form = await readMultipartFormData(event)
  if (!form) throw createError({ statusCode: 400, statusMessage: 'Form data required' })

  const title = form.find(f => f.name === 'title')?.data?.toString()
  const value = form.find(f => f.name === 'value')?.data?.toString()
  const property = form.find(f => f.name === 'property')?.data?.toString()
  const file = form.find(f => f.name === 'file')

  if (!title || !value || !property || !file) throw createError({ statusCode: 400, statusMessage: 'Missing fields' })

  const uploadsDir = join(process.cwd(), 'client', 'public', 'uploads')
  await mkdir(uploadsDir, { recursive: true })
  const safeName = `${Date.now()}-${file.filename || 'invoice.pdf'}`
  const filePath = join(uploadsDir, safeName)
  await writeFile(filePath, file.data)

  const dbPath = join(process.cwd(), 'client', 'server', 'db', 'invoices.json')
  const raw = await readFile(dbPath, 'utf-8').catch(async () => '[]')
  const list = JSON.parse(raw || '[]')

  const record = {
    id: Date.now(),
    title,
    value: parseFloat(value),
    property,
    fileUrl: `/uploads/${safeName}`,
    createdAt: new Date().toISOString()
  }
  list.unshift(record)
  await writeFile(dbPath, JSON.stringify(list, null, 2), 'utf-8')

  return { ok: true, invoice: record }
})


