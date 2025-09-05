export interface Payment {
  id: number
  createdAt: string
  documentType: string
  grossValue: number
  dueDate: string
  receiver: string
  property: string
  status: 'Paid' | 'Pending' | 'Overdue'
}

export const mockPayments: Payment[] = [
  {
    id: 1,
    createdAt: '2024-01-15',
    documentType: 'Rent Invoice',
    grossValue: 2500.00,
    dueDate: '2024-02-01',
    receiver: 'John Smith',
    property: 'Apartament w centrum - A1',
    status: 'Paid'
  },
  {
    id: 2,
    createdAt: '2025-08-20',
    documentType: 'Security Deposit',
    grossValue: 5000.00,
    dueDate: '2025-10-20',
    receiver: 'Maria Kowalski',
    property: 'Dom jednorodzinny - B1',
    status: 'Pending'
  },
  {
    id: 3,
    createdAt: '2024-01-25',
    documentType: 'Rent Invoice',
    grossValue: 1800.00,
    dueDate: '2024-02-01',
    receiver: 'Anna Nowak',
    property: 'Mieszkanie 3-pokojowe - M1',
    status: 'Overdue'
  },
  {
    id: 4,
    createdAt: '2024-02-01',
    documentType: 'Maintenance Fee',
    grossValue: 300.00,
    dueDate: '2024-02-15',
    receiver: 'Piotr Wiśniewski',
    property: 'Apartament premium - C1',
    status: 'Paid'
  },
  {
    id: 5,
    createdAt: '2024-02-05',
    documentType: 'Rent Invoice',
    grossValue: 3200.00,
    dueDate: '2024-03-01',
    receiver: 'Katarzyna Zielińska',
    property: 'Studio w centrum - D2',
    status: 'Pending'
  },
  {
    id: 6,
    createdAt: '2024-02-01',
    documentType: 'Maintenance Fee',
    grossValue: 500.00,
    dueDate: '2024-02-15',
    receiver: 'Piotr Wiśniewski',
    property: 'Apartament premium - C1',
    status: 'Paid'
  }
]
