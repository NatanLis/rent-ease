export default eventHandler(async (event: any) => {
  const propertyId = getRouterParam(event, 'id')

  if (!propertyId) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Property ID is required'
    })
  }

  try {
    const authHeader = getHeader(event, 'authorization')
    if (!authHeader) {
      throw createError({
        statusCode: 401,
        statusMessage: 'No authorization header'
      })
    }

    const response = await fetch(`http://backend:8000/api/units/property/${propertyId}`, {
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
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

    const backendUnits = await response.json()

    // Transform backend data to frontend format
    return backendUnits.map((unit: any) => ({
      id: unit.id,
      propertyId: unit.property_id,
      name: unit.name,
      description: unit.description,
      monthlyRent: unit.monthly_rent,
      propertyTitle: unit.property_title || 'Unknown Property',
      propertyAddress: unit.property_address || 'Unknown Address',
      activeLeases: unit.active_leases || 0,
      status: unit.status || 'available'
    }))
  } catch (error: any) {
    console.error('Error fetching units for property:', error)

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
