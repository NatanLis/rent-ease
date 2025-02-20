<template>
  <div>
    This is random fact about cats:
    <pre>
      {{ data }}
    </pre>

    <button @click="refresh">
      Refresh fact
    </button>
  </div>
</template>
<script setup lang="ts">
const { data, error, refresh } = await useAsyncData(async () => {
  const res = await fetch('/api/cat-fact');
  const data = await res.json();

  return { data };
});
</script>