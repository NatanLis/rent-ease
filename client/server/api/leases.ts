import { getHeader } from 'h3'

// Fetch leases from backend
async function fetchLeases(event: any) {
  // Get auth token from headers
  const authHeader = getHeader(event, 'authorization')

  try {
    if (!authHeader) {
      throw new Error('No authorization header')
    }

    const response = await fetch('http://backend:8000/api/leases/', {
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error(`Failed to fetch leases: ${response.status} ${response.statusText}`)
    }

    const backendLeases = await response.json()

    // Transform backend data to frontend format
    return backendLeases.map((lease: any) => ({
      id: lease.id,
      unitId: lease.unit_id,
      tenantId: lease.tenant_id,
      startDate: lease.start_date,
      endDate: lease.end_date,
      isActive: lease.is_active,
      tenantEmail: lease.user?.email || 'unknown@example.com',
      unitName: lease.unit?.name || `Unit ${lease.unit_id}`,
      propertyTitle: lease.unit?.property?.title || `Property ${lease.unit?.property_id}`,
      propertyAddress: lease.unit?.property?.address || 'Unknown address',
      status: lease.is_active ? 'active' : 'inactive',
      avatar: lease.user?.avatar_url ? {
        src: `http://backend:8000${lease.user.avatar_url}`
      } : {
        src: `https://i.pravatar.cc/128?u=${lease.tenant_id}`
      }
    }))
  } catch (_error) {
    // Fallback to mock data if backend is not available
    return []
  }
}

export default eventHandler(async (event) => {
  // Simulate some delay like real API
  await new Promise(resolve => setTimeout(resolve, 300))

  return await fetchLeases(event)
})
