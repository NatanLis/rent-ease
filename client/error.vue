<template>
  <div class="wrapper">
    <div class="center-container">
      <div class="flex flex-col sm:flex-row justify-center py-5 mb-3">
        <UIcon name="i-heroicons-bolt-slash" class="size-5" />
        <div class="text-3xl text-center font-bold tracking-tight title text-gray-900 dark:text-white sm:text-5xl font-mono">
          Rent<span class="text-primary">ease</span>
        </div>
      </div>
      <div class="text-center">
        <h2 class="font-mono font-bold text-5xl mb-5">{{ error?.statusCode }}</h2>
        <h2 class="font-mono font-bold mb-5">HOUSTON, WE'VE HAD A PROBLEM HERE.</h2>
        <NuxtLink to="/"><UButton>Get back to safety</UButton></NuxtLink>
      </div>
    </div>
  </div>
  <img src="/images/undraw_rocket.svg" alt="Houston, we've had a problem here." class="rocket-img sm:bottom-4 bottom-64" />
</template>

<script setup lang="ts">
import type { NuxtError } from '#app'

const _props = defineProps({
  error: {
    type: Object as () => NuxtError,
    required: true
  }
})
</script>

<style lang="scss" scooped>
.wrapper {
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  z-index: 10;
}

img.rocket-img {
  filter: invert(1);
  width: 50%;
  position: absolute;
  left: 25%;
  opacity: 0.075;
}
</style>
