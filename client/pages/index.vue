<template>
  <div>
    This is the client.
    <pre>
      {{ data }}
    </pre>
  </div>
</template>
<script setup lang="ts">
const { data, error } = await useAsyncData(async () => {
  const res = await fetch('/api');
  const data = await res.json();

  return { data };
});
</script>