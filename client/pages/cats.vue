<template>
  <div>
    This is random fact about cats:
    <pre>
      {{ data }}
    </pre>
  </div>
</template>
<script setup lang="ts">
const { data, error } = await useAsyncData(async () => {
  const res = await fetch('/api/cat-fact');
  const data = await res.json();

  return { data };
});
</script>