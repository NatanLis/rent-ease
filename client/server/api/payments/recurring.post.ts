import { getHeader } from 'h3'

export default eventHandler(async (event: any) => {
  // Only handle POST requests
  if (getMethod(event) !== 'POST') {
    throw createError({
      statusCode: 405,
      statusMessage: 'Method Not Allowed'
    })
  }

  const authHeader = getHeader(event, 'authorization')

  if (!authHeader) {
    throw createError({
      statusCode: 401,
      statusMessage: 'No authorization header'
    })
  }

  const body = await readBody(event)

  try {
    const response = await fetch('http://backend:8000/api/payments/recurring', {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        lease_id: body.leaseId,
        document_type: body.documentType,
        amount: body.amount,
        frequency: body.frequency,
        due_day: body.dueDay,
        description: body.description
      })
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

    // Transform backend response to frontend format
    return {
      leaseId: result.lease_id,
      paymentsCreated: result.payments_created,
      totalAmount: result.total_amount,
      frequency: result.frequency,
      dueDay: result.due_day,
      payments: result.payments
    }
  } catch (error: any) {
    console.error('Error creating recurring payments:', error)

    if (error.statusCode) {
      throw error
    }

    throw createError({
      statusCode: 500,
      statusMessage: 'Internal Server Error',
      data: error.message
    })
  }
})
