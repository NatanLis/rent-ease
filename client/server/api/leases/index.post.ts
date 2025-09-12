export default eventHandler(async (event: any) => {
  if (getMethod(event) !== 'POST') {
    throw createError({
      statusCode: 405,
      statusMessage: 'Method Not Allowed'
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

    const body = await readBody(event)
    console.log('Creating lease with data:', body)

    const response = await fetch('http://backend:8000/api/leases/', {
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
    console.log('Lease created successfully:', result)

    return result
  } catch (error: any) {
    console.error('Error creating lease:', error)

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
