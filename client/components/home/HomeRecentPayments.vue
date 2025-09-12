<script setup lang="ts">
import { h } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { Payment } from '~/data/payments'
import type { Range } from '~/types'

const UBadge = resolveComponent('UBadge')

// Props
interface Props {
  range: Range
  limit?: number
}

const props = withDefaults(defineProps<Props>(), {
  limit: 3
})

const { getToken } = useAuth()
const token = await getToken()

// Pagination state
const pagination = ref({
  pageIndex: 0,
  pageSize: 3
})

// Fetch payments from API
const { data: paymentsData, pending: paymentsPending, refresh: refreshPayments } = await useFetch<Payment[]>('/api/payments', {
  default: () => [],
  server: false,
  headers: token ? {
    'Authorization': `Bearer ${token}`
  } : {}
})

// Filter payments based on date range
const allFilteredPayments = computed(() => {
  if (!paymentsData.value) return []

  const startDate = props.range.start
  const endDate = props.range.end

  return paymentsData.value
    .filter(payment => {
      const paymentDate = new Date(payment.dueDate)
      return paymentDate >= startDate && paymentDate <= endDate
    })
    .sort((a, b) => new Date(b.dueDate).getTime() - new Date(a.dueDate).getTime())
})

// Paginated payments
const paginatedPayments = computed(() => {
  const startIndex = pagination.value.pageIndex * pagination.value.pageSize
  const endIndex = startIndex + pagination.value.pageSize
  return allFilteredPayments.value.slice(startIndex, endIndex)
})

// Total pages
const totalPages = computed(() => {
  return Math.ceil(allFilteredPayments.value.length / pagination.value.pageSize)
})

// Helper functions
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pl-PL', {
    style: 'currency',
    currency: 'PLN'
  }).format(value)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('pl-PL')
}

const getStatusColor = (status: Payment['status']) => {
  const colors = {
    'Paid': 'success' as const,
    'Pending': 'warning' as const,
    'Overdue': 'error' as const
  }
  return colors[status] || 'neutral' as const
}

// Table columns definition (simplified - no select, no actions)
const columns: TableColumn<Payment>[] = [
  {
    accessorKey: 'id',
    header: 'ID',
    cell: ({ row }) => {
      return h('span', { class: 'font-mono text-sm' }, `#${row.original.id}`)
    }
  },
  {
    accessorKey: 'createdAt',
    header: 'Created',
    cell: ({ row }) => {
      return h('span', {}, formatDate(row.original.createdAt))
    }
  },
  {
    accessorKey: 'documentType',
    header: 'Type'
  },
  {
    accessorKey: 'grossValue',
    header: 'Amount',
    cell: ({ row }) => {
      return h('span', { class: 'font-semibold' }, formatCurrency(row.original.grossValue))
    }
  },
  {
    accessorKey: 'dueDate',
    header: 'Due Date',
    cell: ({ row }) => {
      return h('span', {}, formatDate(row.original.dueDate))
    }
  },
  {
    accessorKey: 'receiver',
    header: 'Receiver'
  },
  {
    accessorKey: 'lease.unit.name',
    header: 'Unit',
    cell: ({ row }) => {
      const unitName = row.original.lease?.unit?.name || 'N/A'
      const propertyTitle = row.original.lease?.unit?.property?.title || ''

      return h('div', { class: 'flex flex-col' }, [
        h('span', { class: 'font-medium' }, unitName),
        h('span', { class: 'text-xs text-(--ui-text-muted)' }, propertyTitle)
      ])
    }
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }) => {
      return h(UBadge, {
        class: 'capitalize',
        variant: 'subtle',
        color: getStatusColor(row.original.status)
      }, () => row.original.status)
    }
  }
]

// Watch for range changes to refresh data
watch(() => props.range, () => {
  refreshPayments()
  // Reset to first page when range changes
  pagination.value.pageIndex = 0
}, { deep: true })

// Provide refresh function for parent components
defineExpose({ refresh: refreshPayments })
</script>

<template>
  <UCard>
    <template #header>
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold">Recent Payments</h3>
        <UButton
          to="/home/payments"
          color="primary"
          variant="soft"
          size="xs"
        >
          View all
        </UButton>
      </div>
    </template>

    <div v-if="paymentsPending" class="flex items-center justify-center py-8">
      <UIcon name="i-lucide-loader-2" class="animate-spin size-6" />
    </div>

    <div v-else-if="allFilteredPayments.length === 0" class="text-center py-8 text-(--ui-text-muted)">
      <UIcon name="i-lucide-credit-card" class="size-12 mx-auto mb-4 opacity-40" />
      <p class="text-sm">No payments found for the selected date range</p>
    </div>

    <div v-else>
      <UTable
        :data="paginatedPayments"
        :columns="columns"
        :ui="{
          base: 'table-fixed border-separate border-spacing-0',
          thead: '[&>tr]:bg-(--ui-bg-elevated)/50 [&>tr]:after:content-none',
          tbody: '[&>tr]:last:[&>td]:border-b-0',
          th: 'py-1 first:rounded-l-[calc(var(--ui-radius)*2)] last:rounded-r-[calc(var(--ui-radius)*2)] border-y border-(--ui-border) first:border-l last:border-r',
          td: 'border-b border-(--ui-border)'
        }"
      />

      <!-- Pagination controls -->
      <div v-if="totalPages > 1" class="flex items-center justify-between mt-4 pt-4 border-t border-(--ui-border)">
        <div class="text-sm text-(--ui-text-muted)">
          Showing {{ pagination.pageIndex * pagination.pageSize + 1 }} to {{ Math.min((pagination.pageIndex + 1) * pagination.pageSize, allFilteredPayments.length) }} of {{ allFilteredPayments.length }} payments
        </div>

        <div class="flex items-center gap-2">
          <UButton
            :disabled="pagination.pageIndex === 0"
            color="neutral"
            variant="ghost"
            icon="i-lucide-chevron-left"
            size="sm"
            @click="pagination.pageIndex--"
          />

          <span class="text-sm font-medium">
            {{ pagination.pageIndex + 1 }} / {{ totalPages }}
          </span>

          <UButton
            :disabled="pagination.pageIndex >= totalPages - 1"
            color="neutral"
            variant="ghost"
            icon="i-lucide-chevron-right"
            size="sm"
            @click="pagination.pageIndex++"
          />
        </div>
      </div>
    </div>

    <template v-if="allFilteredPayments.length > 0" #footer>
      <div class="text-sm text-(--ui-text-muted) text-center">
        Total {{ allFilteredPayments.length }} payments from {{ formatDate(range.start.toISOString()) }} to {{ formatDate(range.end.toISOString()) }}
      </div>
    </template>
  </UCard>
</template>
