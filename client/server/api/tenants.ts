import type { User } from '~/types'

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

export default eventHandler(async () => {
  // Simulate some delay like real API
  await new Promise(resolve => setTimeout(resolve, 300))
  
  return tenants
})
