<script setup lang="ts">
const { user } = useUser();

definePageMeta({
  layout: 'dashboard',
})

onBeforeMount(() => {
  if (user.value && !user.value?.isAdmin()) {
    // User is not logged in, redirect to login page
    navigateTo('/home')
  }
})
</script>

<template>
  <UDashboardPanel id="admin">
    <template #header>
      <UDashboardNavbar title="Admin Panel">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="space-y-6">
        <div class="text-center py-12">
          <div class="mx-auto w-24 h-24 bg-primary-100 dark:bg-primary-900/20 rounded-full flex items-center justify-center mb-4">
            <UIcon name="i-lucide-shield-check" class="w-12 h-12 text-primary-600 dark:text-primary-400" />
          </div>
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">Admin Panel</h2>
          <p class="text-gray-600 dark:text-gray-400 max-w-md mx-auto">
            Manage system users, roles, and administrative settings from this central location.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <UCard>
            <template #header>
              <div class="flex items-center gap-3">
                <UIcon name="i-lucide-users" class="w-5 h-5 text-primary-600" />
                <h3 class="font-semibold">Users Management</h3>
              </div>
            </template>
            <p class="text-gray-600 dark:text-gray-400 text-sm mb-4">
              View and manage all system users, their roles and permissions.
            </p>
            <UButton 
              to="/home/admin/users" 
              label="Manage Users" 
              color="primary" 
              variant="outline"
              block
            />
          </UCard>

          <UCard>
            <template #header>
              <div class="flex items-center gap-3">
                <UIcon name="i-lucide-shield" class="w-5 h-5 text-amber-600" />
                <h3 class="font-semibold">Roles & Permissions</h3>
              </div>
            </template>
            <p class="text-gray-600 dark:text-gray-400 text-sm mb-4">
              Configure user roles and system permissions.
            </p>
            <UButton 
              label="Coming Soon" 
              color="gray" 
              variant="outline"
              disabled
              block
            />
          </UCard>

          <UCard>
            <template #header>
              <div class="flex items-center gap-3">
                <UIcon name="i-lucide-settings" class="w-5 h-5 text-green-600" />
                <h3 class="font-semibold">System Settings</h3>
              </div>
            </template>
            <p class="text-gray-600 dark:text-gray-400 text-sm mb-4">
              Configure system-wide settings and preferences.
            </p>
            <UButton 
              label="Coming Soon" 
              color="gray" 
              variant="outline"
              disabled
              block
            />
          </UCard>
        </div>
      </div>
    </template>
  </UDashboardPanel>
</template>
