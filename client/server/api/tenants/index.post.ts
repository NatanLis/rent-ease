import { getHeader, readBody } from 'h3'

export default eventHandler(async (event: any) => {
  const authHeader = getHeader(event, 'authorization')

  if (!authHeader) {
    throw createError({
      statusCode: 401,
      statusMessage: 'No authorization header'
    })
  }

  const body = await readBody(event)

  try {
    const response = await fetch('http://backend:8000/api/tenants/', {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw createError({
        statusCode: response.status,
        statusMessage: response.statusText,
        data: errorData
      })
    }

    const result = await response.json()
    return result
  } catch (error: any) {
    console.error('Error creating tenant:', error)

    if (error.statusCode) {
      throw error
    }

    throw createError({
      statusCode: 500,
      statusMessage: 'Internal server error',
      data: { detail: 'Failed to create tenant' }
    })
  }
})
