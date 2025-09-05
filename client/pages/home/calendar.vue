<template>
  <UDashboardPanel id="calendar">
    <template #header>
      <UDashboardNavbar title="Calendar" :ui="{ right: 'gap-3' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <GoogleCalendar :calendars="calendars" />
    </template>
  </UDashboardPanel>
</template>

<script setup>
import GoogleCalendar from '~/components/GoogleCalendar.vue'


const _value = ref('Backlog')
const _items = ref(['Backlog', 'Todo', 'In Progress', 'Done'])

definePageMeta({
  layout: 'dashboard',
})

// Replace with your real IDs + labels; add/remove as needed.
const calendars = [
  { id: 'kkrol.contact@gmail.com', label: 'Test'},
  { id: 'your_calendar_id_2', label: 'Releases'},
]
</script>
