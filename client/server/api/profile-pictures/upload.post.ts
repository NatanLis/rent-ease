export default eventHandler(async (event) => {
  try {
    const formData = await readMultipartFormData(event)
    
    if (!formData || formData.length === 0) {
      throw createError({
        statusCode: 400,
        statusMessage: 'No file provided'
      })
    }

    const file = formData[0]
    
    if (!file.data || !file.filename) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Invalid file data'
      })
    }

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
    if (!allowedTypes.includes(file.type || '')) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Invalid file type. Only JPG, PNG, and GIF are allowed.'
      })
    }

    // Validate file size (1MB max)
    const maxSize = 1024 * 1024 // 1MB
    if (file.data.length > maxSize) {
      throw createError({
        statusCode: 400,
        statusMessage: 'File too large. Maximum size is 1MB.'
      })
    }

    // Get user ID from headers or session (you'll need to implement auth)
    const userId = getHeader(event, 'x-user-id')
    if (!userId) {
      throw createError({
        statusCode: 401,
        statusMessage: 'User not authenticated'
      })
    }

    // Send file to backend
    const backendFormData = new FormData()
    backendFormData.append('file', new Blob([file.data], { type: file.type }), file.filename)

    const response = await fetch('http://localhost:8000/profile-pictures/upload', {
      method: 'POST',
      headers: {
        'X-User-ID': userId
      },
      body: backendFormData
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw createError({
        statusCode: response.status,
        statusMessage: `Backend error: ${errorText}`
      })
    }

    const result = await response.json()
    
    return {
      success: true,
      profilePicture: {
        id: result.id,
        filename: result.filename,
        mimetype: result.mimetype,
        size: result.size,
        url: `http://localhost:8000/profile-pictures/${result.id}`
      }
    }
  } catch (error) {
    console.error('Profile picture upload error:', error)
    
    if (error.statusCode) {
      throw error
    }
    
    throw createError({
      statusCode: 500,
      statusMessage: 'Internal server error during profile picture upload'
    })
  }
})
