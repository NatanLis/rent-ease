// Mock data for properties - based on the seeds from the database
const properties = [
  {
    id: 1,
    title: 'Apartament w centrum',
    description: 'Nowoczesny apartament w centrum miasta',
    address: 'ul. Główna 1, Warszawa',
    price: 2500,
    ownerId: 1,
    unitsCount: 2,
    activeLeases: 1,
    status: 'active'
  },
  {
    id: 2,
    title: 'Dom jednorodzinny',
    description: 'Przestronny dom z ogrodem',
    address: 'ul. Słoneczna 15, Kraków',
    price: 1800,
    ownerId: 1,
    unitsCount: 2,
    activeLeases: 2,
    status: 'active'
  },
  {
    id: 3,
    title: 'Mieszkanie 3-pokojowe',
    description: 'Komfortowe mieszkanie w spokojnej okolicy',
    address: 'ul. Parkowa 8, Gdańsk',
    price: 2200,
    ownerId: 1,
    unitsCount: 2,
    activeLeases: 1,
    status: 'active'
  },
  {
    id: 4,
    title: 'Apartament premium',
    description: 'Luksusowy apartament z widokiem na miasto',
    address: 'ul. Nowoczesna 25, Wrocław',
    price: 3500,
    ownerId: 1,
    unitsCount: 2,
    activeLeases: 2,
    status: 'active'
  },
  {
    id: 5,
    title: 'Studio w centrum',
    description: 'Kompaktowe studio idealne dla studentów',
    address: 'ul. Studencka 10, Poznań',
    price: 1200,
    ownerId: 1,
    unitsCount: 2,
    activeLeases: 1,
    status: 'active'
  },
  {
    id: 6,
    title: 'Loft przemysłowy',
    description: 'Przestronny loft w stylu industrialnym',
    address: 'ul. Fabryczna 5, Łódź',
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

export default eventHandler(async () => {
  // Simulate some delay like real API
  await new Promise(resolve => setTimeout(resolve, 300))
  
  return properties
})
