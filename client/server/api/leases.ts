import { getHeader } from 'h3'

// Mock data for leases - fallback if backend is not available
const leases = [
  {
    id: 1,
    unitId: 1,
    tenantId: 1,
    startDate: '2024-01-01',
    endDate: '2024-12-31',
    isActive: false,
    tenantEmail: 'tenant1@example.com',
    unitName: 'A1',
    propertyTitle: 'Apartament w centrum',
    propertyAddress: 'ul. Główna 1, Warszawa',
    status: 'inactive'
  },
  {
    id: 2,
    unitId: 2,
    tenantId: 2,
    startDate: '2024-03-01',
    endDate: '2024-09-30',
    isActive: true,
    tenantEmail: 'tenant2@example.com',
    unitName: 'B2',
    propertyTitle: 'Mieszkanie na Mokotowie',
    propertyAddress: 'ul. Mokotowska 10, Warszawa',
    status: 'active'
  },
  {
    id: 3,
    unitId: 3,
    tenantId: 3,
    startDate: '2024-05-15',
    endDate: '2025-05-14',
    isActive: true,
    tenantEmail: 'tenant3@example.com',
    unitName: 'C3',
    propertyTitle: 'Loft na Pradze',
    propertyAddress: 'ul. Praska 5, Warszawa',
    status: 'active'
  },
  {
    id: 4,
    unitId: 4,
    tenantId: 4,
    startDate: '2023-11-01',
    endDate: '2024-10-31',
    isActive: false,
    tenantEmail: 'tenant4@example.com',
    unitName: 'D4',
    propertyTitle: 'Studio na Żoliborzu',
    propertyAddress: 'ul. Żoliborska 8, Warszawa',
    status: 'inactive'
  }
]

// Fetch leases from backend
async function fetchLeases(event: any) {
  // Get auth token from headers
  const authHeader = getHeader(event, 'authorization')
  
  try {
    if (!authHeader) {
      throw new Error('No authorization header')
    }

    const response = await fetch('http://localhost:8000/api/leases/', {
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`Failed to fetch leases: ${response.status} ${response.statusText}`)
    }
    
    const backendLeases = await response.json()
    console.log('Backend leases response:', JSON.stringify(backendLeases, null, 2))
    
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
        src: `http://localhost:8000${lease.user.avatar_url}`
      } : {
        src: `https://i.pravatar.cc/128?u=${lease.tenant_id}`
      }
    }))
  } catch (_error) {
    // Fallback to mock data if backend is not available
    return leases
  }
}

export default eventHandler(async (event) => {
  // Simulate some delay like real API
  await new Promise(resolve => setTimeout(resolve, 300))
  
  return await fetchLeases(event)
})
