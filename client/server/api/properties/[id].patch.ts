export default eventHandler(async (event: any) => {
  // Only handle PATCH requests
  if (getMethod(event) !== 'PATCH') {
    throw createError({
      statusCode: 405,
      statusMessage: 'Method Not Allowed'
    })
  }

  try {
    // Get property ID from route params
    const propertyId = getRouterParam(event, 'id')
    if (!propertyId) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Property ID is required'
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
    console.log('Updating property with ID:', propertyId, 'with data:', body)

    // Forward to backend
    const response = await fetch(`http://backend:8000/api/properties/${propertyId}`, {
      method: 'PATCH',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    })

    if (!response.ok) {
      const errorData = await response.text()
      console.error('Backend error:', response.status, errorData)
      throw createError({
        statusCode: response.status,
        statusMessage: `Backend error: ${response.statusText}`,
        data: errorData
      })
    }

    const result = await response.json()
    console.log('Property updated successfully:', result)

    return result
  } catch (error: any) {
    console.error('Error updating property:', error)

    // If it's already a createError, re-throw it
    if (error.statusCode) {
      throw error
    }

    // Otherwise create a new error
    throw createError({
      statusCode: 500,
      statusMessage: 'Internal Server Error',
      data: error.message
    })
  }
})
