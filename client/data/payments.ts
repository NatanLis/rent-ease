export interface Payment {
  id: number
  createdAt: string
  documentType: string
  grossValue: number
  dueDate: string
  receiver: string
  lease?: {
    id: number
    unit_id: number
    tenant_id: number
    user: {
      id: number
      email: string
      first_name: string
      last_name: string
      avatar_url?: string
    }
    unit: {
      id: number
      name: string
      monthly_rent: number
      property: {
        id: number
        title: string
        address: string
      }
    }
  },
  status: 'Paid' | 'Pending' | 'Overdue'
  description?: string
  isPaid: boolean
  invoiceFileUrl?: string
  invoiceFileName?: string
}

export interface RecurringPaymentCreate {
  leaseId: number
  documentType: string
  amount: number
  frequency: 'monthly' | 'quarterly' | 'yearly'
  dueDay: number
  description?: string
}

export interface RecurringPaymentResponse {
  leaseId: number
  paymentsCreated: number
  totalAmount: number
  frequency: 'monthly' | 'quarterly' | 'yearly'
  dueDay: number
  payments: number[]
}
