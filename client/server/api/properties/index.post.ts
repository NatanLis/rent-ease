export default eventHandler(async (event) => {
  // Only handle POST requests
  if (getMethod(event) !== 'POST') {
    throw createError({
      statusCode: 405,
      statusMessage: 'Method Not Allowed'
    })
  }

  try {
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
    console.log('Creating property with data:', body)

    // Forward to backend
    const response = await fetch('http://backend:8000/api/properties/', {
      method: 'POST',
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
    console.log('Property created successfully:', result)

    return result
  } catch (error) {
    console.error('Error creating property:', error)

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
