interface AdminUser {
  id: number
  name: string
  email: string
  role: 'ADMIN' | 'OWNER' | 'TENANT'
  status: 'active' | 'inactive'
  avatar?: {
    src: string
  }
  location: string
  createdAt: string
}

// Mock data for admin users - based on the seeds from the database
const adminUsers: AdminUser[] = [
  {
    id: 1,
    name: 'Admin User',
    email: 'admin@rent-ease.com',
    role: 'ADMIN',
    status: 'active',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=admin'
    },
    location: 'Warszawa, Poland',
    createdAt: '2024-01-15T10:00:00Z'
  },
  {
    id: 2,
    name: 'Jan Kowalski',
    email: 'owner1@example.com',
    role: 'OWNER',
    status: 'active',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=owner1'
    },
    location: 'Kraków, Poland',
    createdAt: '2024-01-20T14:30:00Z'
  },
  {
    id: 3,
    name: 'Anna Nowak',
    email: 'owner2@example.com',
    role: 'OWNER',
    status: 'active',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=owner2'
    },
    location: 'Gdańsk, Poland',
    createdAt: '2024-02-01T09:15:00Z'
  },
  {
    id: 4,
    name: 'Piotr Wiśniewski',
    email: 'tenant1@example.com',
    role: 'TENANT',
    status: 'active',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=tenant1'
    },
    location: 'Wrocław, Poland',
    createdAt: '2024-02-10T16:45:00Z'
  },
  {
    id: 5,
    name: 'Maria Kowalczyk',
    email: 'tenant2@example.com',
    role: 'TENANT',
    status: 'active',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=tenant2'
    },
    location: 'Poznań, Poland',
    createdAt: '2024-02-15T11:20:00Z'
  },
  {
    id: 6,
    name: 'Tomasz Zieliński',
    email: 'tenant3@example.com',
    role: 'TENANT',
    status: 'inactive',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=tenant3'
    },
    location: 'Łódź, Poland',
    createdAt: '2024-02-20T13:10:00Z'
  },
  {
    id: 7,
    name: 'Katarzyna Lewandowska',
    email: 'tenant4@example.com',
    role: 'TENANT',
    status: 'active',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=tenant4'
    },
    location: 'Katowice, Poland',
    createdAt: '2024-03-01T08:30:00Z'
  },
  {
    id: 8,
    name: 'Michał Dąbrowski',
    email: 'tenant5@example.com',
    role: 'TENANT',
    status: 'active',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=tenant5'
    },
    location: 'Lublin, Poland',
    createdAt: '2024-03-05T15:45:00Z'
  },
  {
    id: 9,
    name: 'Agnieszka Kamińska',
    email: 'tenant6@example.com',
    role: 'TENANT',
    status: 'inactive',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=tenant6'
    },
    location: 'Białystok, Poland',
    createdAt: '2024-03-10T12:00:00Z'
  },
  {
    id: 10,
    name: 'Paweł Szymański',
    email: 'tenant7@example.com',
    role: 'TENANT',
    status: 'active',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=tenant7'
    },
    location: 'Szczecin, Poland',
    createdAt: '2024-03-15T10:15:00Z'
  },
  {
    id: 11,
    name: 'Magdalena Woźniak',
    email: 'tenant8@example.com',
    role: 'TENANT',
    status: 'active',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=tenant8'
    },
    location: 'Gdynia, Poland',
    createdAt: '2024-03-20T14:20:00Z'
  },
  {
    id: 12,
    name: 'Robert Kozłowski',
    email: 'tenant9@example.com',
    role: 'TENANT',
    status: 'inactive',
    avatar: {
      src: 'https://i.pravatar.cc/128?u=tenant9'
    },
    location: 'Radom, Poland',
    createdAt: '2024-03-25T09:30:00Z'
  }
]

export default eventHandler(async () => {
  // Simulate some delay like real API
  await new Promise(resolve => setTimeout(resolve, 300))
  
  return adminUsers
})
