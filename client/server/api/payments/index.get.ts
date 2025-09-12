export default eventHandler(async (event: any) => {
  const authHeader = getHeader(event, 'authorization')

  if (!authHeader) {
    throw createError({
      statusCode: 401,
      statusMessage: 'No authorization header'
    })
  }

  try {
    const response = await fetch('http://backend:8000/api/payments/', {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      }
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

    // Transform backend data to frontend format
    return result.map((payment: any) => ({
      id: payment.id,
      createdAt: payment.created_at,
      documentType: payment.document_type,
      grossValue: payment.gross_value,
      dueDate: payment.due_date,
      receiver: payment.receiver,
      description: payment.description,
      isPaid: payment.is_paid,
      status: payment.status,
      invoiceFileUrl: payment.invoice_file?.id ? `/api/files/${payment.invoice_file.id}/download` : null,
      invoiceFileName: payment.invoice_file?.filename || null,
      lease: payment.lease ? {
        id: payment.lease.id,
        unit_id: payment.lease.unit_id,
        tenant_id: payment.lease.tenant_id,
        user: {
          id: payment.lease.user.id,
          email: payment.lease.user.email,
          first_name: payment.lease.user.first_name,
          last_name: payment.lease.user.last_name,
          avatar_url: payment.lease.user.avatar_url ? `http://backend:8000${payment.lease.user.avatar_url}` : undefined
        },
        unit: {
          id: payment.lease.unit.id,
          name: payment.lease.unit.name,
          monthly_rent: payment.lease.unit.monthly_rent,
          property: {
            id: payment.lease.unit.property.id,
            title: payment.lease.unit.property.title,
            address: payment.lease.unit.property.address
          }
        }
      } : undefined
    }))
  } catch (error: any) {
    console.error('Error fetching payments:', error)

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
