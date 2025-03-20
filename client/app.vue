<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup lang="ts">
const config = useRuntimeConfig();
const colorMode = useColorMode()

</script>

<style scss>
html {
  background-color: rgb(var(--color-gray-200));
}
</style>
