<script setup lang="ts">
import { eachDayOfInterval, eachWeekOfInterval, eachMonthOfInterval, format, addDays } from 'date-fns'
import { VisXYContainer, VisLine, VisAxis, VisArea, VisCrosshair, VisTooltip } from '@unovis/vue'
import type { Period, Range } from '~/types'
import type { Payment } from '~/data/payments'

const cardRef = useTemplateRef<HTMLElement | null>('cardRef')

const props = defineProps<{
  period: Period
  range: Range
}>()

type DataRecord = {
  date: Date
  amount: number
}

const { getToken } = useAuth()
const token = await getToken()

// Fetch payments from API
const { data: paymentsData } = await useFetch<Payment[]>('/api/payments', {
  default: () => [],
  server: false,
  headers: token ? {
    'Authorization': `Bearer ${token}`
  } : {}
})

// Build chart data from payments (sum of PAID grossValue per bucket)
const { data } = await useAsyncData<DataRecord[]>(async () => {
  const dates = ({
    daily: eachDayOfInterval,
    weekly: eachWeekOfInterval,
    monthly: eachMonthOfInterval
  } as Record<Period, typeof eachDayOfInterval>)[props.period](props.range)

  // Get only PAID payments and filter by dueDate (when payment was supposed to be paid)
  const paidPayments = (paymentsData.value as Payment[])
    .filter(p => p.status === 'Paid')
    .map(p => ({ ...p, dueDateParsed: new Date(p.dueDate) }))

  const records: DataRecord[] = []

  for (let i = 0; i < dates.length; i++) {
    const start = new Date(dates[i])
    start.setHours(0, 0, 0, 0)
    const nextBoundary = i < dates.length - 1 ? new Date(dates[i + 1]) : addDays(new Date(props.range.end), 1)
    nextBoundary.setHours(0, 0, 0, 0)

    const amount = paidPayments
      .filter(p => p.dueDateParsed >= start && p.dueDateParsed < nextBoundary)
      .reduce((sum, p) => sum + (Number(p.grossValue) || 0), 0)

    records.push({ date: start, amount })
  }

  return records
}, {
  watch: [() => props.period, () => props.range, paymentsData],
  default: () => []
})

const x = (_: DataRecord, i: number) => i
const y = (d: DataRecord) => d.amount

const total = computed(() => data.value.reduce((acc: number, { amount }) => acc + amount, 0))

const formatNumber = new Intl.NumberFormat('pl-PL', { style: 'currency', currency: 'PLN', maximumFractionDigits: 0 }).format

const formatDate = (date: Date): string => {
  return ({
    daily: format(date, 'd MMM'),
    weekly: format(date, 'd MMM'),
    monthly: format(date, 'MMM yyy')
  })[props.period]
}

const xTicks = (i: number) => {
  if (i === 0 || i === data.value.length - 1 || !data.value[i]) {
    return ''
  }

  return formatDate(data.value[i].date)
}

const template = (d: DataRecord) => `${formatDate(d.date)}: ${formatNumber(d.amount)}`
</script>

<template>
  <UCard ref="cardRef" :ui="{ body: '!px-0 !pt-0 !pb-3' }">
    <template #header>
      <div>
        <p class="text-xs text-(--ui-text-muted) uppercase mb-1.5">
          Revenue
        </p>
        <p class="text-3xl text-(--ui-text-highlighted) font-semibold">
          {{ formatNumber(total) }}
        </p>
      </div>
    </template>

    <VisXYContainer
      :data="data"
      :padding="{ top: 40 }"
      class="h-96"
    >
      <VisLine
        :x="x"
        :y="y"
        color="var(--ui-primary)"
      />
      <VisArea
        :x="x"
        :y="y"
        color="var(--ui-primary)"
        :opacity="0.1"
      />

      <VisAxis
        type="x"
        :x="x"
        :tick-format="xTicks"
      />

      <VisCrosshair
        color="var(--ui-primary)"
        :template="template"
      />

      <VisTooltip />
    </VisXYContainer>
  </UCard>
</template>

<style scoped>
.unovis-xy-container {
  --vis-crosshair-line-stroke-color: var(--ui-primary);
  --vis-crosshair-circle-stroke-color: var(--ui-bg);

  --vis-axis-grid-color: var(--ui-border);
  --vis-axis-tick-color: var(--ui-border);
  --vis-axis-tick-label-color: var(--ui-text-dimmed);

  --vis-tooltip-background-color: var(--ui-bg);
  --vis-tooltip-border-color: var(--ui-border);
  --vis-tooltip-text-color: var(--ui-text-highlighted);
}
</style>
