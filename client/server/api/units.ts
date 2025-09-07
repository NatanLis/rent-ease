import { getHeader } from 'h3'

// Mock data for units - based on the seeds from the database
// COMMENTED OUT - using real backend data instead
/*
const units = [
  {
    id: 1,
    propertyId: 1,
    name: '[MOCK] A1',
    description: 'Apartament 1-pokojowy z balkonem - MOCK DATA',
    monthlyRent: 2500,
    propertyTitle: '[MOCK] Apartament w centrum',
    propertyAddress: 'ul. Mockowa 1, Mockowo',
    activeLeases: 0,
    status: 'available'
  },
  {
    id: 2,
    propertyId: 1,
    name: '[MOCK] A2',
    description: 'Apartament 2-pokojowy z tarasem - MOCK DATA',
    monthlyRent: 3000,
    propertyTitle: '[MOCK] Apartament w centrum',
    propertyAddress: 'ul. Mockowa 1, Mockowo',
    activeLeases: 1,
    status: 'occupied'
  },
  {
    id: 3,
    propertyId: 2,
    name: '[MOCK] B1',
    description: 'Dom jednorodzinny - parter - MOCK DATA',
    monthlyRent: 1800,
    propertyTitle: '[MOCK] Dom jednorodzinny',
    propertyAddress: 'ul. Mockowa 15, Mockowo',
    activeLeases: 1,
    status: 'occupied'
  },
  {
    id: 4,
    propertyId: 2,
    name: 'B2',
    description: 'Dom jednorodzinny - piętro',
    monthlyRent: 2000,
    propertyTitle: 'Dom jednorodzinny',
    propertyAddress: 'ul. Słoneczna 15, Kraków',
    activeLeases: 1,
    status: 'occupied'
  },
  {
    id: 5,
    propertyId: 3,
    name: 'C1',
    description: 'Mieszkanie 3-pokojowe - salon',
    monthlyRent: 2200,
    propertyTitle: 'Mieszkanie 3-pokojowe',
    propertyAddress: 'ul. Parkowa 8, Gdańsk',
    activeLeases: 1,
    status: 'occupied'
  },
  {
    id: 6,
    propertyId: 3,
    name: 'C2',
    description: 'Mieszkanie 3-pokojowe - sypialnia',
    monthlyRent: 1800,
    propertyTitle: 'Mieszkanie 3-pokojowe',
    propertyAddress: 'ul. Parkowa 8, Gdańsk',
    activeLeases: 0,
    status: 'available'
  },
  {
    id: 7,
    propertyId: 4,
    name: 'D1',
    description: 'Apartament premium - widok na miasto',
    monthlyRent: 3500,
    propertyTitle: 'Apartament premium',
    propertyAddress: 'ul. Nowoczesna 25, Wrocław',
    activeLeases: 1,
    status: 'occupied'
  },
  {
    id: 8,
    propertyId: 4,
    name: 'D2',
    description: 'Apartament premium - widok na park',
    monthlyRent: 3200,
    propertyTitle: 'Apartament premium',
    propertyAddress: 'ul. Nowoczesna 25, Wrocław',
    activeLeases: 1,
    status: 'occupied'
  },
  {
    id: 9,
    propertyId: 5,
    name: 'E1',
    description: 'Studio - kompaktowe',
    monthlyRent: 1200,
    propertyTitle: 'Studio w centrum',
    propertyAddress: 'ul. Studencka 10, Poznań',
    activeLeases: 1,
    status: 'occupied'
  },
  {
    id: 10,
    propertyId: 5,
    name: 'E2',
    description: 'Studio - przestronne',
    monthlyRent: 1400,
    propertyTitle: 'Studio w centrum',
    propertyAddress: 'ul. Studencka 10, Poznań',
    activeLeases: 0,
    status: 'available'
  },
  {
    id: 11,
    propertyId: 6,
    name: 'F1',
    description: 'Loft - przestronny',
    monthlyRent: 2800,
    propertyTitle: 'Loft przemysłowy',
    propertyAddress: 'ul. Fabryczna 5, Łódź',
    activeLeases: 1,
    status: 'occupied'
  },
  {
    id: 12,
    propertyId: 6,
    name: 'F2',
    description: 'Loft - kompaktowy',
    monthlyRent: 2200,
    propertyTitle: 'Loft przemysłowy',
    propertyAddress: 'ul. Fabryczna 5, Łódź',
    activeLeases: 0,
    status: 'available'
  },
  {
    id: 13,
    propertyId: 7,
    name: 'G1',
    description: 'Kamienica - parter',
    monthlyRent: 1600,
    propertyTitle: 'Kamienica zabytkowa',
    propertyAddress: 'ul. Stara 12, Lublin',
    activeLeases: 0,
    status: 'available'
  },
  {
    id: 14,
    propertyId: 7,
    name: 'G2',
    description: 'Kamienica - piętro',
    monthlyRent: 1800,
    propertyTitle: 'Kamienica zabytkowa',
    propertyAddress: 'ul. Stara 12, Lublin',
    activeLeases: 0,
    status: 'available'
  },
  {
    id: 15,
    propertyId: 7,
    name: 'G3',
    description: 'Kamienica - poddasze',
    monthlyRent: 1400,
    propertyTitle: 'Kamienica zabytkowa',
    propertyAddress: 'ul. Stara 12, Lublin',
    activeLeases: 0,
    status: 'available'
  },
  {
    id: 16,
    propertyId: 8,
    name: 'H1',
    description: 'Apartament nad morzem - widok na plażę',
    monthlyRent: 4200,
    propertyTitle: 'Apartament nad morzem',
    propertyAddress: 'ul. Nadmorska 7, Sopot',
    activeLeases: 1,
    status: 'occupied'
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

    const response = await fetch('http://localhost:8000/units/', {
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }
    
    const backendUnits = await response.json()
    console.log('Backend units response:', JSON.stringify(backendUnits, null, 2))
    
    // Transform backend data to frontend format
    return backendUnits.map((unit: any) => ({
      id: unit.id,
      propertyId: unit.property_id,
      name: unit.name,
      description: unit.description,
      monthlyRent: unit.monthly_rent,
      propertyTitle: unit.property?.title || 'Unknown Property',
      propertyAddress: unit.property?.address || 'Unknown Address',
      activeLeases: 0, // TODO: Calculate from leases
      status: 'available' // TODO: Calculate based on active leases
    }))
  } catch (error) {
    console.error('Error fetching units from backend:', error)
    console.error('Error details:', error)
    console.log('No fallback data - returning empty array')
    // No fallback - return empty array if backend is not available
    return []
  }
})
