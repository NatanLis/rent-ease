import { getHeader } from 'h3'

// Fetch all leases from backend (admin only)
async function fetchAllLeases(event: any) {
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
      throw new Error(`Failed to fetch all leases: ${response.status} ${response.statusText}`)
    }

    const backendLeases = await response.json()

    // Transform backend data to frontend format
    return backendLeases.map((lease: any) => ({
      id: lease.id,
      unit_id: lease.unit_id,
      tenant_id: lease.tenant_id,
      start_date: lease.start_date,
      end_date: lease.end_date,
      is_active: lease.is_active,
      user: {
        id: lease.user?.id || 0,
        email: lease.user?.email || 'unknown@example.com',
        first_name: lease.user?.first_name || 'Unknown',
        last_name: lease.user?.last_name || 'User',
        avatar_url: lease.user?.avatar_url ? `http://backend:8000${lease.user.avatar_url}` : undefined
      },
      unit: {
        id: lease.unit?.id || 0,
        name: lease.unit?.name || 'Unknown Unit',
        monthly_rent: lease.unit?.monthly_rent || 0,
        property: {
          id: lease.unit?.property?.id || 0,
          title: lease.unit?.property?.title || 'Unknown Property',
          address: lease.unit?.property?.address || 'Unknown address'
        }
      }
    }))
  } catch (error) {
    console.error('Error fetching all leases from backend:', error)
    console.error('Error details:', error)
    console.log('Auth header:', authHeader)
    console.log('No fallback data - returning empty array')
    // No fallback - return empty array if backend is not available
    return []
  }
}

export default eventHandler(async (event) => {
  // Simulate some delay like real API
  await new Promise(resolve => setTimeout(resolve, 300))

  return await fetchAllLeases(event)
})
