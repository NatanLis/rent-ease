export default eventHandler(async (event: any) => {
  // Only handle DELETE requests
  if (getMethod(event) !== 'DELETE') {
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

    console.log('Deleting property with ID:', propertyId)

    // Forward to backend
    const response = await fetch(`http://backend:8000/api/properties/${propertyId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      const errorData = await response.text()
      console.error('Backend error:', response.status, errorData)

      // Parse error message if it's JSON
      let errorDetail = errorData
      try {
        const errorJson = JSON.parse(errorData)
        errorDetail = errorJson.detail || errorData
      } catch {
        // Keep original error if not JSON
      }

      throw createError({
        statusCode: response.status,
        statusMessage: `Backend error: ${response.statusText}`,
        data: { detail: errorDetail }
      })
    }

    console.log('Property deleted successfully')
    return { success: true }
  } catch (error: any) {
    console.error('Error deleting property:', error)

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
