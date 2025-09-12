export default eventHandler(async (event: any) => {
  // Only handle PATCH requests
  if (getMethod(event) !== 'PATCH') {
    throw createError({
      statusCode: 405,
      statusMessage: 'Method Not Allowed'
    })
  }

  const unitId = getRouterParam(event, 'id')
  const body = await readBody(event)

  try {
    // Get auth token from headers
    const authHeader = getHeader(event, 'authorization')
    if (!authHeader) {
      throw createError({
        statusCode: 401,
        statusMessage: 'No authorization header'
      })
    }

    // Transform frontend data to backend format
    const backendData = {
      property_id: body.property_id,
      name: body.name,
      description: body.description,
      monthly_rent: body.monthly_rent
      // Note: status is calculated automatically by backend
    }

    const response = await fetch(`http://backend:8000/api/units/${unitId}`, {
      method: 'PATCH',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(backendData)
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw createError({
        statusCode: response.status,
        statusMessage: errorData.detail || `Backend responded with status: ${response.status}`
      })
    }

    const updatedUnit = await response.json()

    // Transform backend response to frontend format
    return {
      id: updatedUnit.id,
      propertyId: updatedUnit.property_id,
      name: updatedUnit.name,
      description: updatedUnit.description,
      monthlyRent: updatedUnit.monthly_rent,
      propertyTitle: updatedUnit.property_title || 'Unknown Property',
      propertyAddress: updatedUnit.property_address || 'Unknown Address',
      activeLeases: updatedUnit.active_leases || 0,
      status: updatedUnit.status || 'available'
    }
  } catch (error: any) {
    console.error('Error updating unit:', error)

    if (error.statusCode) {
      throw error
    }

    throw createError({
      statusCode: 500,
      statusMessage: 'Internal server error while updating unit'
    })
  }
})
