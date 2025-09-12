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

  try {
    const formData = await readMultipartFormData(event)
    if (!formData) {
      throw createError({
        statusCode: 400,
        statusMessage: 'No form data received'
      })
    }

    // Extract form fields
    const documentType = formData.find((f: any) => f.name === 'documentType')?.data?.toString()
    const grossValue = formData.find((f: any) => f.name === 'grossValue')?.data?.toString()
    const dueDate = formData.find((f: any) => f.name === 'dueDate')?.data?.toString()
    const receiver = formData.find((f: any) => f.name === 'receiver')?.data?.toString()
    const description = formData.find((f: any) => f.name === 'description')?.data?.toString()
    const leaseId = formData.find((f: any) => f.name === 'leaseId')?.data?.toString()
    const invoiceFile = formData.find((f: any) => f.name === 'invoiceFile')

    if (!documentType || !grossValue || !dueDate || !receiver || !leaseId) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Missing required fields'
      })
    }

    let invoiceFileId = null

    // Handle file upload if provided
    if (invoiceFile && invoiceFile.data) {
      // Upload file to files API first
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
      invoiceFileId = uploadedFile.id

      console.log('Invoice file uploaded:', uploadedFile.filename, 'ID:', uploadedFile.id)
    }

    // Create payment data
    const paymentData = {
      document_type: documentType,
      gross_value: parseFloat(grossValue),
      due_date: dueDate,
      receiver: receiver,
      description: description || '',
      lease_id: parseInt(leaseId),
      invoice_file_id: invoiceFileId
    }

    // Send to backend
    const response = await fetch('http://backend:8000/api/payments/', {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(paymentData)
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
      invoiceFileName: result.invoice_file?.filename || null,
      lease: result.lease ? {
        id: result.lease.id,
        unit_id: result.lease.unit_id,
        tenant_id: result.lease.tenant_id,
        user: {
          id: result.lease.user.id,
          email: result.lease.user.email,
          first_name: result.lease.user.first_name,
          last_name: result.lease.user.last_name,
          avatar_url: result.lease.user.avatar_url ? `http://backend:8000${result.lease.user.avatar_url}` : undefined
        },
        unit: {
          id: result.lease.unit.id,
          name: result.lease.unit.name,
          monthly_rent: result.lease.unit.monthly_rent,
          property: {
            id: result.lease.unit.property.id,
            title: result.lease.unit.property.title,
            address: result.lease.unit.property.address
          }
        }
      } : undefined
    }

  } catch (error: any) {
    console.error('Error creating payment with invoice:', error)

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
