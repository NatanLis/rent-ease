export default defineEventHandler(async (event) => {
  const leaseId = getRouterParam(event, 'id')

  if (!leaseId) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Lease ID is required'
    })
  }

  try {
    // Get authorization header from the request
    const authHeader = getHeader(event, 'authorization')

    // Use Docker service name for backend communication
    const backendUrl = 'http://backend:8000'

    const response = await $fetch(`${backendUrl}/api/leases/${leaseId}/activate`, {
      method: 'PATCH',
      headers: {
        'Authorization': authHeader || '',
        'Content-Type': 'application/json'
      }
    })

    return response
  } catch (error: any) {
    console.error('Error activating lease:', error)

    if (error?.status) {
      throw createError({
        statusCode: error.status,
        statusMessage: error.statusText || 'Failed to activate lease'
      })
    }

    throw createError({
      statusCode: 500,
      statusMessage: 'Internal Server Error'
    })
  }
})
