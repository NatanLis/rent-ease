import { getHeader } from 'h3'

// Fetch tenants from backend
async function fetchTenants(event: any) {
  // Get auth token from headers
  const authHeader = getHeader(event, 'authorization')

  try {
    if (!authHeader) {
      throw new Error('No authorization header')
    }
    const response = await fetch('http://backend:8000/api/tenants/', {
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error(`Failed to fetch tenants: ${response.status} ${response.statusText}`)
    }

    const users = await response.json()
    // Return data as-is since component uses first_name/last_name directly
    return users.map((user: any) => ({
      ...user,
      // Add computed fields if needed for consistency
      location: user.location || 'Poland'
    }))
  } catch (error) {
    console.error('Error fetching tenants from backend:', error)
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

  return await fetchTenants(event)
})
