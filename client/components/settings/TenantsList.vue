<script setup lang="ts">
import type { Tenant } from '~/types'

defineProps<{
  tenants: Tenant[]
}>()

const items = [{
  label: 'Edit tenant',
  onSelect: () => console.log('Edit tenant')
}, {
  label: 'View contract',
  onSelect: () => console.log('View contract')
}, {
  label: 'Remove tenant',
  color: 'error' as const,
  onSelect: () => console.log('Remove tenant')
}]

const getStatusColor = (status: string) => {
  switch (status) {
    case 'active':
      return 'green'
    case 'expired':
      return 'red'
    case 'pending':
      return 'yellow'
    case 'terminated':
      return 'gray'
    default:
      return 'gray'
  }
}

const getStatusLabel = (status: string) => {
  switch (status) {
    case 'active':
      return 'Active'
    case 'expired':
      return 'Expired'
    case 'pending':
      return 'Pending'
    case 'terminated':
      return 'Terminated'
    default:
      return status
  }
}
</script>

<template>
  <ul role="list" class="divide-y divide-(--ui-border)">
    <li
      v-for="(tenant, index) in tenants"
      :key="index"
      class="flex items-center justify-between gap-3 py-3 px-4 sm:px-6"
    >
      <div class="flex items-center gap-3 min-w-0">
        <UAvatar
          v-bind="tenant.avatar"
          size="md"
        />

        <div class="text-sm min-w-0">
          <p class="text-(--ui-text-highlighted) font-medium truncate">
            {{ tenant.name }}
          </p>
          <p class="text-(--ui-text-muted) truncate">
            {{ tenant.email }}
          </p>
          <p class="text-(--ui-text-muted) text-xs truncate">
            {{ tenant.property }} - {{ tenant.unit }}
          </p>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <div class="text-right">
          <UBadge
            :color="getStatusColor(tenant.contractStatus)"
            variant="subtle"
            size="sm"
          >
            {{ getStatusLabel(tenant.contractStatus) }}
          </UBadge>
          <p class="text-xs text-(--ui-text-muted) mt-1">
            {{ tenant.contractStartDate }} - {{ tenant.contractEndDate }}
          </p>
        </div>

        <UDropdownMenu :items="items" :content="{ align: 'end' }">
          <UButton
            icon="i-lucide-ellipsis-vertical"
            color="neutral"
            variant="ghost"
          />
        </UDropdownMenu>
      </div>
    </li>
  </ul>
</template>
