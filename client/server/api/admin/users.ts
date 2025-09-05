interface AdminUser {
  id: number
  firstName: string
  lastName: string
  email: string
  role: 'admin' | 'owner' | 'tenant'
  status: 'active' | 'inactive'
  avatar?: {
    src: string
  }
  createdAt: string
}

// Mock data for admin users - based on the seeds from the database
const adminUsers: AdminUser[] = [
  {
    id: 1,
    firstName: 'Admin',
    lastName: 'User',
    email: 'admin@rent-ease.com',
    role: 'admin',
    status: 'active',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=admin'
    },
    createdAt: '2024-01-15T10:00:00Z'
  },
  {
    id: 2,
    firstName: 'Jan',
    lastName: 'Kowalski',
    email: 'owner1@example.com',
    role: 'owner',
    status: 'active',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=owner1'
    },
    createdAt: '2024-01-20T14:30:00Z'
  },
  {
    id: 3,
    firstName: 'Anna',
    lastName: 'Nowak',
    email: 'owner2@example.com',
    role: 'owner',
    status: 'active',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=owner2'
    },
    createdAt: '2024-02-01T09:15:00Z'
  },
  {
    id: 4,
    firstName: 'Piotr',
    lastName: 'Wiśniewski',
    email: 'tenant1@example.com',
    role: 'tenant',
    status: 'active',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=tenant1'
    },
    createdAt: '2024-02-10T16:45:00Z'
  },
  {
    id: 5,
    firstName: 'Maria',
    lastName: 'Kowalczyk',
    email: 'tenant2@example.com',
    role: 'tenant',
    status: 'active',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=tenant2'
    },
    createdAt: '2024-02-15T11:20:00Z'
  },
  {
    id: 6,
    firstName: 'Tomasz',
    lastName: 'Zieliński',
    email: 'tenant3@example.com',
    role: 'tenant',
    status: 'inactive',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=tenant3'
    },
    createdAt: '2024-02-20T13:10:00Z'
  },
  {
    id: 7,
    firstName: 'Katarzyna',
    lastName: 'Lewandowska',
    email: 'tenant4@example.com',
    role: 'tenant',
    status: 'active',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=tenant4'
    },
    createdAt: '2024-03-01T08:30:00Z'
  },
  {
    id: 8,
    firstName: 'Michał',
    lastName: 'Dąbrowski',
    email: 'tenant5@example.com',
    role: 'tenant',
    status: 'active',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=tenant5'
    },
    createdAt: '2024-03-05T15:45:00Z'
  },
  {
    id: 9,
    firstName: 'Agnieszka',
    lastName: 'Kamińska',
    email: 'tenant6@example.com',
    role: 'tenant',
    status: 'inactive',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=tenant6'
    },
    createdAt: '2024-03-10T12:00:00Z'
  },
  {
    id: 10,
    firstName: 'Paweł',
    lastName: 'Szymański',
    email: 'tenant7@example.com',
    role: 'tenant',
    status: 'active',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=tenant7'
    },
    createdAt: '2024-03-15T10:15:00Z'
  },
  {
    id: 11,
    firstName: 'Magdalena',
    lastName: 'Woźniak',
    email: 'tenant8@example.com',
    role: 'tenant',
    status: 'active',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=tenant8'
    },
    createdAt: '2024-03-20T14:20:00Z'
  },
  {
    id: 12,
    firstName: 'Robert',
    lastName: 'Kozłowski',
    email: 'tenant9@example.com',
    role: 'tenant',
    status: 'inactive',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=tenant9'
    },
    createdAt: '2024-03-25T09:30:00Z'
  }
]

// Fetch users from backend
async function fetchUsers(event: any) {
  try {
    // Get token from request headers
    const authHeader = getHeader(event, 'authorization')
    const token = authHeader?.replace('Bearer ', '')
    
    console.log('Token received:', token ? 'Yes' : 'No')
    console.log('Auth header:', authHeader)
    console.log('Token value:', token)
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    }
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    
    const response = await fetch('http://localhost:8000/users/', {
      headers
    })
    
    if (!response.ok) {
      throw new Error(`Failed to fetch users: ${response.status} ${response.statusText}`)
    }
    const users = await response.json()
    
    // Transform backend data to frontend format
    return users.map((user: any) => ({
      id: user.id,
      firstName: user.first_name,
      lastName: user.last_name,
      email: user.email,
      role: user.role,
      status: user.is_active ? 'active' : 'inactive',
      avatar: user.profile_picture_id ? {
        src: `http://localhost:8000/profile-pictures/${user.profile_picture_id}`
      } : undefined,
      createdAt: user.created_at
    }))
  } catch (error) {
    console.error('Error fetching users from backend:', error)
    // Fallback to mock data if backend is not available
    return adminUsers
  }
}

export default eventHandler(async (event) => {
  // Simulate some delay like real API
  await new Promise(resolve => setTimeout(resolve, 300))
  
  return await fetchUsers(event)
})
