import type { User } from '~/types'
import { getHeader } from 'h3'

// Mock data for tenants - based on the seeds from the database
const tenants: User[] = [
  {
    id: 1,
    name: 'tenant1',
    email: 'tenant1@example.com',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=1'
    },
    status: 'inactive', // Has leases but all inactive
    location: 'Warszawa, Poland'
  },
  {
    id: 2,
    name: 'tenant2', 
    email: 'tenant2@example.com',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=2'
    },
    status: 'active', // Has active leases
    location: 'Kraków, Poland'
  },
  {
    id: 3,
    name: 'tenant3',
    email: 'tenant3@example.com',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=3'
    },
    status: 'active',
    location: 'Gdańsk, Poland'
  },
  {
    id: 4,
    name: 'tenant4',
    email: 'tenant4@example.com',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=4'
    },
    status: 'inactive',
    location: 'Wrocław, Poland'
  },
  {
    id: 5,
    name: 'tenant5',
    email: 'tenant5@example.com',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=5'
    },
    status: 'active',
    location: 'Poznań, Poland'
  },
  {
    id: 6,
    name: 'tenant6',
    email: 'tenant6@example.com',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=6'
    },
    status: 'inactive',
    location: 'Łódź, Poland'
  },
  {
    id: 7,
    name: 'tenant7',
    email: 'tenant7@example.com',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=7'
    },
    status: 'active',
    location: 'Katowice, Poland'
  },
  {
    id: 8,
    name: 'tenant8',
    email: 'tenant8@example.com',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=8'
    },
    status: 'active',
    location: 'Lublin, Poland'
  },
  {
    id: 9,
    name: 'tenant9',
    email: 'tenant9@example.com',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=9'
    },
    status: 'inactive',
    location: 'Białystok, Poland'
  },
  {
    id: 10,
    name: 'tenant10',
    email: 'tenant10@example.com',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=10'
    },
    status: 'active',
    location: 'Szczecin, Poland'
  }
]

// Fetch tenants from backend
async function fetchTenants(event: any) {
  try {
    // Get auth token from headers
    const authHeader = getHeader(event, 'authorization')
    if (!authHeader) {
      throw new Error('No authorization header')
    }

    const response = await fetch('http://localhost:8000/users/?role=tenant', {
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`Failed to fetch tenants: ${response.status} ${response.statusText}`)
    }
    
    const users = await response.json()
    
    // Transform backend data to frontend format
    return users.map((user: any) => ({
      id: user.id,
      name: `${user.first_name} ${user.last_name}`,
      email: user.email,
      avatar: user.avatar_url ? {
        src: `http://localhost:8000${user.avatar_url}`
      } : undefined, // Will show fallback icon
      status: user.is_active ? 'active' : 'inactive',
      location: user.location || 'Poland' // Use location from backend or default
    }))
  } catch (error) {
    console.error('Error fetching tenants from backend:', error)
    console.error('Error details:', error)
    console.log('Auth header:', authHeader)
    console.log('Falling back to mock data')
    // Fallback to mock data if backend is not available
    return tenants
  }
}

export default eventHandler(async (event) => {
  // Simulate some delay like real API
  await new Promise(resolve => setTimeout(resolve, 300))
  
  return await fetchTenants(event)
})
