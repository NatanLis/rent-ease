import type { User } from '~/types'
import { getHeader } from 'h3'

// Mock data for tenants - based on the seeds from the database
// COMMENTED OUT - using real backend data instead
/*
const tenants: User[] = [
  {
    id: 1,
    name: '[MOCK] tenant1',
    email: 'tenant1@mock.com',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=1'
    },
    status: 'inactive',
    location: 'Warszawa, Poland'
  },
  // ... more mock data
]
*/

// Fetch all tenants from backend (admin only)
async function fetchAllTenants(event: any) {
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
      throw new Error(`Failed to fetch all tenants: ${response.status} ${response.statusText}`)
    }

    const users = await response.json()

    // Transform backend data to frontend format
    return users.map((user: any) => ({
      id: user.id,
      name: `${user.first_name} ${user.last_name}`,
      email: user.email,
      avatar: user.avatar_url ? {
        src: `http://backend:8000${user.avatar_url}`
      } : undefined, // Will show fallback icon
      status: user.is_active ? 'active' : 'inactive',
      location: user.location || 'Poland' // Use location from backend or default
    }))
  } catch (error) {
    console.error('Error fetching all tenants from backend:', error)
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

  return await fetchAllTenants(event)
})
