<template>
  <section class="w-full">
    <h1>Company Calendar</h1>
    <GoogleCalendar :calendars="calendars" :initialView="'MONTH'" :startOnMonday="true" />
  </section>
</template>

<script setup>
import GoogleCalendar from '~/components/GoogleCalendar.vue'

definePageMeta({
  layout: 'dashboard',
})

// Replace with your real IDs + labels; add/remove as needed.
const calendars = [
  { id: 'kkrol.contact@gmail.com', label: 'Test', color: '#4285F4' },
  { id: 'your_calendar_id_2', label: 'Releases',      color: '#DB4437' },
]


</script>