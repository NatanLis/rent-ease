<template>
  <div class="gc">
    <!-- Calendar picker (single select) -->
    <USelect
      v-model="selectedId"
      :items="selectItems"
      placeholder="Select a calendar"
      class="w-60 mb-3"
    />

    <!-- View toggles -->
    <div class="gc__toolbar">

      <UButton
        :color="view == 'MONTH' ? 'primary' : 'secondary'"
        :variant="view == 'MONTH' ? 'solid' : 'outline'"
        @click="view = 'MONTH'"
        label="Month"/>

      <UButton :color="view == 'WEEK' ? 'primary' : 'secondary'"
        :variant="view == 'WEEK' ? 'solid' : 'outline'"
        @click="view = 'WEEK'"
        label="Week"/>

      <UButton :color="view == 'AGENDA' ? 'primary' : 'secondary'"
        :variant="view == 'AGENDA' ? 'solid' : 'outline'"
        @click="view = 'AGENDA'"
        label="Agenda"/>
    </div>


    <!-- Render only on client to avoid SSR timezone flicker -->
    <ClientOnly>
      <div class="gc__frame">
        <iframe
          :src="iframeSrc"
          title="Google Calendar"
          frameborder="0"
          scrolling="no"
          aria-label="Embedded Google Calendar"
          referrerpolicy="no-referrer-when-downgrade"
        />
      </div>
    </ClientOnly>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  calendars: {
    type: Array,
    required: true,
    default: () => []
  }
})

const selectedId = ref('')
const view = ref('MONTH')
const tz = ref('UTC')

onMounted(() => {
  // Client-only: detect timezone & language
  try {
    tz.value = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'
    lang.value = (navigator.language || 'en').split('-')[0]
  } catch (e) {}
    if (props.defaultCalendarId) {
    selectedId.value = props.defaultCalendarId
  } else if (props.calendars.length > 0) {
    selectedId.value = props.calendars[0].id
  }
})



const selectItems = computed(() => {
  // If your calendar objects use different keys, adapt here (e.g. name/id)
  return props.calendars.map(c => ({ label: c.label, value: c.id }))
})

const iframeSrc = computed(() => {
  if (!selectedId.value) return ''
  const params = new URLSearchParams()
  params.set('ctz', tz.value)
  params.set('mode', view.value)      // MONTH | WEEK | AGENDA
  params.set('showTitle', '0')
  params.set('showTabs', '0')
  params.set('showPrint', '0')
  params.set('bgcolor', '#ffffff')
  params.append('src', selectedId.value)
  return `https://calendar.google.com/calendar/embed?${params.toString()}`
})
</script>

<style lang="scss" scoped>
/* Layout & responsiveness */
.gc {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.gc__select {
  margin-bottom: 0.5rem;
}

.gc__toolbar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.gc__toolbar button {
  padding: 0.35rem 0.6rem;
  border: 1px solid #ddd;
  border-radius: 0.4rem;
  cursor: pointer;
}

.gc__toolbar button.active {
  font-weight: 600;
  text-decoration: underline;
}

/* Full-height iframe */
.gc__frame {
  flex: 1; /* take remaining vertical space */
  width: 100%;
  position: relative;
}

.gc__frame iframe {
  border: 0;
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
