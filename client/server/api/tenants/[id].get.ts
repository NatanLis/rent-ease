export default eventHandler(async (event: any) => {
  const authHeader = getHeader(event, 'authorization')

  if (!authHeader) {
    throw createError({
      statusCode: 401,
      statusMessage: 'No authorization header'
    })
  }

  const tenantId = getRouterParam(event, 'id')

  if (!tenantId) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Tenant ID is required'
    })
  }

  try {
    const response = await fetch(`http://backend:8000/api/tenants/${tenantId}`, {
      method: 'GET',
      headers: {
        'Authorization': authHeader
      }
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw createError({
        statusCode: response.status,
        statusMessage: response.statusText,
        data: errorData
      })
    }

    const user = await response.json()

    // Transform backend data to frontend format
    return {
      id: user.id,
      name: `${user.first_name} ${user.last_name}`,
      email: user.email,
      avatar: user.avatar_url ? {
        src: `http://backend:8000${user.avatar_url}`
      } : undefined,
      status: user.is_active ? 'active' : 'inactive',
      location: user.location || 'Poland'
    }
  } catch (error: any) {
    console.error('Error fetching tenant:', error)

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
