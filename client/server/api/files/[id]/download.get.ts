export default eventHandler(async (event: any) => {
  const fileId = getRouterParam(event, 'id')
  const authHeader = getHeader(event, 'authorization')

  if (!fileId) {
    throw createError({
      statusCode: 400,
      statusMessage: 'File ID is required'
    })
  }

  if (!authHeader) {
    throw createError({
      statusCode: 401,
      statusMessage: 'No authorization header'
    })
  }

  try {
    // Forward request to backend
    const response = await fetch(`http://backend:8000/api/files/${fileId}/download`, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
      }
    })

    if (!response.ok) {
      throw createError({
        statusCode: response.status,
        statusMessage: response.statusText
      })
    }

    // Get file data and headers
    const fileData = await response.arrayBuffer()
    const contentType = response.headers.get('content-type') || 'application/octet-stream'
    const contentDisposition = response.headers.get('content-disposition') || 'attachment; filename=file'

    // Return file with proper headers
    setHeader(event, 'content-type', contentType)
    setHeader(event, 'content-disposition', contentDisposition)

    return new Uint8Array(fileData)

  } catch (error: any) {
    console.error('Error downloading file:', error)

    if (error.statusCode) {
      throw error
    }

    throw createError({
      statusCode: 500,
      statusMessage: 'Internal Server Error',
      data: { detail: error.message }
    })
  }
})
