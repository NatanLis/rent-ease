<template>
  <div class="gc">
    <!-- Calendar picker (checkboxes) -->
    <label v-for="c in calendars" :key="c.id">
    <input type="checkbox" :value="c.id" v-model="selectedIds" />
    {{ c.label }}
  </label>

    <!-- View toggles -->
    <div class="gc__toolbar">
      <button :class="{ active: view === 'MONTH' }" @click="view = 'MONTH'">Month</button>
      <button :class="{ active: view === 'WEEK' }"  @click="view = 'WEEK'">Week</button>
      <button :class="{ active: view === 'AGENDA' }" @click="view = 'AGENDA'">Agenda</button>
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
        ></iframe>
      </div>
    </ClientOnly>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  calendars: {
    type: Array,
    default: () => ([
      { id: 'your_calendar_id_1', label: 'Work',     color: '#4285F4' },
      { id: 'your_calendar_id_2', label: 'Personal', color: '#34A853' },
    ])
  },
  startOnMonday: { type: Boolean, default: true },
  initialView:   { type: String,  default: 'MONTH' } 
})

const selectedId = ref(props.calendars[0]?.id || '')
const view = ref(props.initialView)
const tz = ref('UTC')
const lang = ref('en')

onMounted(() => {
  // Client-only: detect timezone & language
  try {
    tz.value = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'
    lang.value = (navigator.language || 'en').split('-')[0]
  } catch (e) {}
})

const iframeSrc = computed(() => {
  const params = new URLSearchParams()
  params.set('ctz', tz.value)            
  params.set('mode', view.value)          
  if (props.startOnMonday) params.set('wkst', '1') 
  params.set('bgcolor', '#ffffff')        
  params.set('showTitle', '0')            
  params.set('showPrint', '0')            
  params.set('showTabs', '0')             
  params.set('showTz', '0')               
  params.set('hl', lang.value)            

  // Selected calendar
  if (selectedId.value) {
    params.append('src', selectedId.value)
    const cal = props.calendars.find(c => c.id === selectedId.value)
    if (cal?.color) params.append('color', cal.color) // color is paired with the last src
  }

  return `https://calendar.google.com/calendar/embed?${params.toString()}`
})
</script>

<style scoped>
/* Layout & responsiveness */
.gc__frame {
  width: 100%;
  aspect-ratio: 4 / 3;          /* modern responsive approach */
  position: relative;
}
.gc__frame iframe {
  border: 0;
  width: 100%;
  height: 100%;
  position: absolute; inset: 0;
}

/* Controls */
.gc__select { margin: .25rem 0; }
.gc__toolbar { display: flex; gap: .5rem; margin: .5rem 0 1rem; }
.gc__toolbar button { padding: .35rem .6rem; border: 1px solid #ddd; border-radius: .4rem; }
.gc__toolbar button.active { font-weight: 600; text-decoration: underline; }

/* Mobile: make it squarer to avoid overscroll */
@media (max-width: 640px) {
  .gc__frame { aspect-ratio: 1 / 1; }
}

/* Accessibility helper for the select label */
.sr-only {
  position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
  overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0;
}
</style>
