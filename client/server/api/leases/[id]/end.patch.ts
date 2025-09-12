export default defineEventHandler(async (event: any) => {
  // Get lease ID from route params
  const leaseId = getRouterParam(event, 'id')

  if (!leaseId) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Lease ID is required'
    })
  }

  // Get auth token from headers
  const authHeader = getHeader(event, 'authorization')

  if (!authHeader) {
    throw createError({
      statusCode: 401,
      statusMessage: 'No authorization header'
    })
  }

  // Get request body
  const body = await readBody(event)

  try {
    // In Docker container, use service name 'backend'
    const backendUrl = 'http://backend:8000'

    const response = await fetch(`${backendUrl}/api/leases/${leaseId}/end`, {
      method: 'PATCH',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    })


    if (!response.ok) {
      const errorText = await response.text()
      throw createError({
        statusCode: response.status,
        statusMessage: `Failed to end lease: ${response.statusText}`,
        data: errorText
      })
    }
    const result = await response.json()

    // Transform backend response to frontend format if needed
    return {
      id: result.id,
      unit_id: result.unit_id,
      tenant_id: result.tenant_id,
      start_date: result.start_date,
      end_date: result.end_date,
      is_active: result.is_active,
      user: result.user,
      unit: result.unit
    }

  } catch (error: any) {
    console.error('[LEASE END] Error details:', {
      message: error.message,
      name: error.name,
      cause: error.cause,
      stack: error.stack
    })

    if (error.statusCode) {
      throw error
    }

    // Check if it's a network error
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw createError({
        statusCode: 503,
        statusMessage: 'Cannot connect to backend service. Please check if the backend is running.'
      })
    }

    throw createError({
      statusCode: 500,
      statusMessage: 'Internal server error while ending lease',
      data: error.message
    })
  }
})
