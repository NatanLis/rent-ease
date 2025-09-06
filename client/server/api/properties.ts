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
  {
    id: 2,
    title: '[MOCK] Dom jednorodzinny',
    description: 'Przestronny dom z ogrodem - MOCK DATA',
    address: 'ul. Mockowa 15, Mockowo',
    price: 1800,
    ownerId: 1,
    unitsCount: 2,
    activeLeases: 2,
    status: 'active'
  },
  {
    id: 3,
    title: '[MOCK] Mieszkanie 3-pokojowe',
    description: 'Komfortowe mieszkanie w spokojnej okolicy - MOCK DATA',
    address: 'ul. Mockowa 8, Mockowo',
    price: 2200,
    ownerId: 1,
    unitsCount: 2,
    activeLeases: 1,
    status: 'active'
  },
  {
    id: 4,
    title: '[MOCK] Apartament premium',
    description: 'Luksusowy apartament z widokiem na miasto - MOCK DATA',
    address: 'ul. Mockowa 25, Mockowo',
    price: 3500,
    ownerId: 1,
    unitsCount: 2,
    activeLeases: 2,
    status: 'active'
  },
  {
    id: 5,
    title: '[MOCK] Studio w centrum',
    description: 'Kompaktowe studio idealne dla studentów - MOCK DATA',
    address: 'ul. Mockowa 10, Mockowo',
    price: 1200,
    ownerId: 1,
    unitsCount: 2,
    activeLeases: 1,
    status: 'active'
  },
  {
    id: 6,
    title: '[MOCK] Loft przemysłowy',
    description: 'Przestronny loft w stylu industrialnym - MOCK DATA',
    address: 'ul. Mockowa 5, Mockowo',
    price: 2800,
    ownerId: 1,
    unitsCount: 2,
    activeLeases: 1,
    status: 'active'
  },
  {
    id: 7,
    title: 'Kamienica zabytkowa',
    description: 'Odrestaurowana kamienica z duszą',
    address: 'ul. Stara 12, Lublin',
    price: 1600,
    ownerId: 1,
    unitsCount: 3,
    activeLeases: 0,
    status: 'available'
  },
  {
    id: 8,
    title: 'Apartament nad morzem',
    description: 'Apartament z widokiem na morze',
    address: 'ul. Nadmorska 7, Sopot',
    price: 4200,
    ownerId: 1,
    unitsCount: 1,
    activeLeases: 1,
    status: 'active'
  }
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

    // Get user role from token to determine which endpoint to use
    // For now, we'll use the owner endpoint as default since most users are owners
    // In a real app, you'd decode the JWT token to get the role
    const response = await fetch('http://localhost:8000/api/properties/owner', {
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }
    
    const backendProperties = await response.json()
    console.log('Backend properties response:', JSON.stringify(backendProperties, null, 2))
    
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
    console.error('Error fetching properties from backend:', error)
    console.error('Error details:', error)
    console.log('No fallback data - returning empty array')
    // No fallback - return empty array if backend is not available
    return []
  }
})
