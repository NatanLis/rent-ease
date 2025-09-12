export default eventHandler(async (event: any) => {
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
    console.log('Creating unit with data:', body)

    // Forward to backend
    const response = await fetch('http://backend:8000/api/units/', {
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

    const result = await response.json()
    console.log('Unit created successfully:', result)

    return result
  } catch (error: any) {
    console.error('Error creating unit:', error)

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
