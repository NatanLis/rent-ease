<template>
  <UCard>
    This is random fact about cats:
    <pre>
      {{ data?.data.fact }}
    </pre>

    <UButton @click="refresh">
      Refresh fact
    </UButton>
  </UCard>
</template>
<script setup lang="ts">
const { data, error, refresh } = await useAsyncData(async () => {
  const res = await fetch('/api/cat-fact');
  const data = await res.json();

  return { data };
});
</script>