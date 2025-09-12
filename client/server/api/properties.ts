import { getHeader } from 'h3'


export default eventHandler(async (event) => {
  // Simulate some delay like real API
  await new Promise(resolve => setTimeout(resolve, 300))

  try {
    // Get auth token from headers
    const authHeader = getHeader(event, 'authorization')
    if (!authHeader) {
      throw new Error('No authorization header')
    }

    // Get user role from token to determine which endpoint to use
    // For now, we'll use the owner endpoint as default since most users are owners
    // In a real app, you'd decode the JWT token to get the role
    const response = await fetch('http://backend:8000/api/properties/', {
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const backendProperties = await response.json()

    // Transform backend data to frontend format
    return backendProperties.map((property: any) => ({
      id: property.id,
      title: property.title,
      description: property.description,
      address: property.address,
      price: property.price,
      ownerId: property.owner_id,
      unitsCount: property.units_count,
      activeLeases: property.active_leases,
      status: 'active'
    }))
  } catch (error) {
    console.error('Error fetching properties from backend:', error)
    console.error('Error details:', error)
    console.log('No fallback data - returning empty array')
    // No fallback - return empty array if backend is not available
    return []
  }
})
