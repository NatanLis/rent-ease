export default eventHandler(async (event) => {
  try {
    const id = getRouterParam(event, 'id')

    if (!id) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Profile picture ID is required'
      })
    }

    // Fetch profile picture from backend
    const response = await fetch(`http://backend:8000/profile-pictures/${id}`)

    if (!response.ok) {
      if (response.status === 404) {
        throw createError({
          statusCode: 404,
          statusMessage: 'Profile picture not found'
        })
      }

      throw createError({
        statusCode: response.status,
        statusMessage: 'Backend error'
      })
    }

    const fileData = await response.arrayBuffer()
    const contentType = response.headers.get('content-type') || 'application/octet-stream'

    // Set appropriate headers
    setHeader(event, 'Content-Type', contentType)
    setHeader(event, 'Cache-Control', 'public, max-age=31536000') // Cache for 1 year

    return new Uint8Array(fileData)
  } catch (error) {
    console.error('Profile picture fetch error:', error)

    if (error.statusCode) {
      throw error
    }

    throw createError({
      statusCode: 500,
      statusMessage: 'Internal server error during profile picture fetch'
    })
  }
})
