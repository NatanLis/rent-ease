<template>
  <UCard class="text-primary-500">
    This is the client.
    <pre>
      {{ data }}
    </pre>
    
    <UButton variant="soft" nuxt-to="/cats">
      Click me to learn
    </UButton>
  </UCard>
</template>
<script setup lang="ts">
const { data, error } = await useAsyncData(async () => {
  const res = await fetch('/api');
  const data = await res.json();

  return { data };
});
</script>