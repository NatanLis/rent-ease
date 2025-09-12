export default eventHandler(async (event: any) => {
  // Only handle PATCH requests
  if (getMethod(event) !== 'PATCH') {
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

  const paymentId = getRouterParam(event, 'id')
  const body = await readBody(event)

  if (!paymentId) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Payment ID is required'
    })
  }

  try {
    const response = await fetch(`http://backend:8000/api/payments/${paymentId}/status`, {
      method: 'PATCH',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        is_paid: body.isPaid
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
      id: result.id,
      createdAt: result.created_at,
      documentType: result.document_type,
      grossValue: result.gross_value,
      dueDate: result.due_date,
      receiver: result.receiver,
      description: result.description,
      isPaid: result.is_paid,
      status: result.status,
      lease: result.lease ? {
        id: result.lease.id,
        unit_id: result.lease.unit_id,
        tenant_id: result.lease.tenant_id,
        user: {
          id: result.lease.user.id,
          email: result.lease.user.email,
          first_name: result.lease.user.first_name,
          last_name: result.lease.user.last_name,
          avatar_url: result.lease.user.avatar_url ? `http://backend:8000${result.lease.user.avatar_url}` : undefined
        },
        unit: {
          id: result.lease.unit.id,
          name: result.lease.unit.name,
          monthly_rent: result.lease.unit.monthly_rent,
          property: {
            id: result.lease.unit.property.id,
            title: result.lease.unit.property.title,
            address: result.lease.unit.property.address
          }
        }
      } : undefined
    }
  } catch (error: any) {
    console.error('Error updating payment status:', error)

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
