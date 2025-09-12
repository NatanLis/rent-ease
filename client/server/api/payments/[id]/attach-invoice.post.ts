export default eventHandler(async (event: any) => {
  // Only handle POST requests
  if (getMethod(event) !== 'POST') {
    throw createError({
      statusCode: 405,
      statusMessage: 'Method Not Allowed'
    })
  }

  const authHeader = getHeader(event, 'authorization')

  if (!authHeader) {
    throw createError({
      statusCode: 401,
      statusMessage: 'No authorization header'
    })
  }

  const paymentId = getRouterParam(event, 'id')

  if (!paymentId) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Payment ID is required'
    })
  }

  try {
    const formData = await readMultipartFormData(event)
    if (!formData) {
      throw createError({
        statusCode: 400,
        statusMessage: 'No form data received'
      })
    }

    const invoiceFile = formData.find((f: any) => f.name === 'invoiceFile')

    if (!invoiceFile || !invoiceFile.data) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Invoice file is required'
      })
    }

    // First, upload the file to the files API
    const fileFormData = new FormData()
    const blob = new Blob([invoiceFile.data], { type: invoiceFile.type || 'application/pdf' })
    fileFormData.append('file', blob, invoiceFile.filename || 'invoice.pdf')

    const fileUploadResponse = await fetch('http://backend:8000/api/files/', {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
      },
      body: fileFormData
    })

    if (!fileUploadResponse.ok) {
      const errorData = await fileUploadResponse.json().catch(() => ({ detail: 'File upload failed' }))
      throw createError({
        statusCode: fileUploadResponse.status,
        statusMessage: 'File upload failed',
        data: errorData
      })
    }

    const uploadedFile = await fileUploadResponse.json()

    // Now attach the file to the payment
    const response = await fetch(`http://backend:8000/api/payments/${paymentId}/attach-invoice`, {
      method: 'PATCH',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        invoice_file_id: uploadedFile.id
      })
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw createError({
        statusCode: response.status,
        statusMessage: response.statusText,
        data: errorData
      })
    }

    const result = await response.json()

    // Transform backend response to frontend format
    return {
      id: result.id,
      createdAt: result.created_at,
      documentType: result.document_type,
      grossValue: result.gross_value,
      dueDate: result.due_date,
      receiver: result.receiver,
      description: result.description,
      isPaid: result.is_paid,
      status: result.status,
      invoiceFileUrl: result.invoice_file?.id ? `/api/files/${result.invoice_file.id}/download` : null,
      invoiceFileName: result.invoice_file?.filename || null
    }

  } catch (error: any) {
    console.error('Error attaching invoice to payment:', error)

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
