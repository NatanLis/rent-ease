<template>
  <UCard>
    This is random fact about cats:
    <pre>
      {{ data?.data.fact }}
    </pre>
    <UButton
      label="Button"
      color="secondary"
      size="lg"
      @click="() => refresh()"
    />
  </UCard>
</template>

<script setup lang="ts">
const { data, refresh } = await useAsyncData(async () => {
  const res = await fetch('/api/cat-fact');
  const data = await res.json();

  return { data };
});
</script>