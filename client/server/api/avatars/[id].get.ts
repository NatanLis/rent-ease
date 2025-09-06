export default eventHandler(async (event) => {
  try {
    const id = getRouterParam(event, 'id')
    
    if (!id) {
      throw createError({
        statusCode: 400,
        statusMessage: 'File ID is required'
      })
    }

    // Fetch file from backend
    const response = await fetch(`http://localhost:8000/files/${id}`)
    
    if (!response.ok) {
      if (response.status === 404) {
        throw createError({
          statusCode: 404,
          statusMessage: 'File not found'
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
    console.error('Avatar fetch error:', error)
    
    if (error.statusCode) {
      throw error
    }
    
    throw createError({
      statusCode: 500,
      statusMessage: 'Internal server error during file fetch'
    })
  }
})
