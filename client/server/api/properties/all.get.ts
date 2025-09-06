import { getHeader } from 'h3'

// Mock data for properties - based on the seeds from the database
// COMMENTED OUT - using real backend data instead
/*
const properties = [
  {
    id: 1,
    title: '[MOCK] Apartament w centrum',
    description: 'Nowoczesny apartament w centrum miasta - MOCK DATA',
    address: 'ul. Mockowa 1, Mockowo',
    price: 2500,
    ownerId: 1,
    unitsCount: 2,
    activeLeases: 1,
    status: 'active'
  },
  // ... more mock data
]
*/

export default eventHandler(async (event) => {
  // Simulate some delay like real API
  await new Promise(resolve => setTimeout(resolve, 300))
  
  try {
    // Get auth token from headers
    const authHeader = getHeader(event, 'authorization')
    if (!authHeader) {
      throw new Error('No authorization header')
    }

    const response = await fetch('http://localhost:8000/api/properties/', {
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }
    
    const backendProperties = await response.json()
    console.log('Backend all properties response:', JSON.stringify(backendProperties, null, 2))
    
    // Transform backend data to frontend format
    return backendProperties.map((property: any) => ({
      id: property.id,
      title: property.title,
      description: property.description,
      address: property.address,
      price: property.price,
      ownerId: property.owner_id,
      unitsCount: 0, // TODO: Calculate from units
      activeLeases: 0, // TODO: Calculate from leases
      status: 'active'
    }))
  } catch (error) {
    console.error('Error fetching all properties from backend:', error)
    console.error('Error details:', error)
    console.log('No fallback data - returning empty array')
    // No fallback - return empty array if backend is not available
    return []
  }
})
