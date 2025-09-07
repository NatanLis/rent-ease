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


const value = ref('Backlog')
const items = ref(['Backlog', 'Todo', 'In Progress', 'Done'])

definePageMeta({
  layout: 'dashboard',
})

// Replace with your real IDs + labels; add/remove as needed.
const calendars = [
  { id: 'rentease2137@gmail.com', label: 'Test'},
  { id: '846dbd0ce509e14824e55daedcbfe0d03140a3b952777acfe7bcac10ebaae3af@group.calendar.google.com', label: 'Apartment1'},
]
</script>

