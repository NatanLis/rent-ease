// Mock data for leases - based on the seeds from the database
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
    startDate: '2024-01-01',
    endDate: '2024-12-31',
    isActive: true,
    tenantEmail: 'tenant2@example.com',
    unitName: 'A2',
    propertyTitle: 'Apartament w centrum',
    propertyAddress: 'ul. Główna 1, Warszawa',
    status: 'active'
  },
  {
    id: 3,
    unitId: 3,
    tenantId: 3,
    startDate: '2024-02-01',
    endDate: '2025-01-31',
    isActive: true,
    tenantEmail: 'tenant3@example.com',
    unitName: 'B1',
    propertyTitle: 'Dom jednorodzinny',
    propertyAddress: 'ul. Słoneczna 15, Kraków',
    status: 'active'
  },
  {
    id: 4,
    unitId: 4,
    tenantId: 4,
    startDate: '2024-03-01',
    endDate: '2025-02-28',
    isActive: true,
    tenantEmail: 'tenant4@example.com',
    unitName: 'B2',
    propertyTitle: 'Dom jednorodzinny',
    propertyAddress: 'ul. Słoneczna 15, Kraków',
    status: 'active'
  },
  {
    id: 5,
    unitId: 5,
    tenantId: 5,
    startDate: '2024-04-01',
    endDate: '2025-03-31',
    isActive: true,
    tenantEmail: 'tenant5@example.com',
    unitName: 'M1',
    propertyTitle: 'Mieszkanie 3-pokojowe',
    propertyAddress: 'ul. Parkowa 8, Gdańsk',
    status: 'active'
  },
  {
    id: 6,
    unitId: 6,
    tenantId: 6,
    startDate: '2023-06-01',
    endDate: '2024-05-31',
    isActive: false,
    tenantEmail: 'tenant6@example.com',
    unitName: 'M2',
    propertyTitle: 'Mieszkanie 3-pokojowe',
    propertyAddress: 'ul. Parkowa 8, Gdańsk',
    status: 'inactive'
  },
  {
    id: 7,
    unitId: 7,
    tenantId: 7,
    startDate: '2024-05-01',
    endDate: '2025-04-30',
    isActive: true,
    tenantEmail: 'tenant7@example.com',
    unitName: 'C1',
    propertyTitle: 'Apartament premium',
    propertyAddress: 'ul. Nowoczesna 25, Wrocław',
    status: 'active'
  },
  {
    id: 8,
    unitId: 8,
    tenantId: 8,
    startDate: '2024-06-01',
    endDate: '2025-05-31',
    isActive: true,
    tenantEmail: 'tenant8@example.com',
    unitName: 'C2',
    propertyTitle: 'Apartament premium',
    propertyAddress: 'ul. Nowoczesna 25, Wrocław',
    status: 'active'
  },
  {
    id: 9,
    unitId: 9,
    tenantId: 9,
    startDate: '2023-08-01',
    endDate: '2024-07-31',
    isActive: false,
    tenantEmail: 'tenant9@example.com',
    unitName: 'D1',
    propertyTitle: 'Studio w centrum',
    propertyAddress: 'ul. Studencka 10, Poznań',
    status: 'inactive'
  },
  {
    id: 10,
    unitId: 10,
    tenantId: 10,
    startDate: '2024-07-01',
    endDate: '2025-06-30',
    isActive: true,
    tenantEmail: 'tenant10@example.com',
    unitName: 'D2',
    propertyTitle: 'Studio w centrum',
    propertyAddress: 'ul. Studencka 10, Poznań',
    status: 'active'
  },
  {
    id: 11,
    unitId: 11,
    tenantId: 1,
    startDate: '2024-08-01',
    endDate: '2025-07-31',
    isActive: true,
    tenantEmail: 'tenant1@example.com',
    unitName: 'E1',
    propertyTitle: 'Loft przemysłowy',
    propertyAddress: 'ul. Fabryczna 5, Łódź',
    status: 'active'
  },
  {
    id: 12,
    unitId: 12,
    tenantId: 2,
    startDate: '2023-09-01',
    endDate: '2024-08-31',
    isActive: false,
    tenantEmail: 'tenant2@example.com',
    unitName: 'E2',
    propertyTitle: 'Loft przemysłowy',
    propertyAddress: 'ul. Fabryczna 5, Łódź',
    status: 'inactive'
  }
]

export default eventHandler(async () => {
  // Simulate some delay like real API
  await new Promise(resolve => setTimeout(resolve, 300))

  return leases
})
