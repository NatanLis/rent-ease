<script setup lang="ts">
const toast = useToast();
const { getToken } = useAuth();
const { user } = useUser();

const open = ref(false);

const showItem = (active: boolean | undefined) => {
  return active ? '' : 'hidden'
}

const links = [
  {
  label: 'Home',
  icon: 'i-lucide-house',
  to: '/home',
  onSelect: () => {
    open.value = false
  }
}, {
  label: 'Inbox',
  icon: 'i-lucide-inbox',
  to: '/home/inbox',
  badge: '4',
  onSelect: () => {
    open.value = false
  }
}, {
  label: 'Calendar',
  icon: 'i-lucide-calendar',
  to: '/home/calendar',
  onSelect: () => {
    open.value = false
   }
}, {
  label: 'Tenants',
  icon: 'i-lucide-users',
  to: '/home/tenants',
  class: showItem(!user.value?.isTenant()),
  onSelect: () => {
    open.value = false
  }
}, {
  label: 'Leases',
  icon: 'i-lucide-file-text',
  to: '/home/leases',
  // class: showItem(!user.value?.isTenant()),
  onSelect: () => {
    open.value = false
  }
}, {
  label: 'Properties',
  icon: 'i-lucide-building',
  to: '/home/properties',
  class: showItem(!user.value?.isTenant()),
  onSelect: () => {
    open.value = false
  }
}, {
  label: 'Units',
  icon: 'i-lucide-home',
  to: '/home/units',
  class: showItem(!user.value?.isTenant()),
  onSelect: () => {
    open.value = false
  }
}, {
  label: 'Payments',
  icon: 'i-lucide-credit-card',
  to: '/home/payments',
  onSelect: () => {
    open.value = false
  }
}, {
  label: 'Invoices',
  icon: 'i-lucide-receipt',
  to: '/home/invoices',
  class: 'hidden',
  onSelect: () => {
    open.value = false
  }
}, {
  label: 'Admin Panel',
  to: '/home/admin',
  icon: 'i-lucide-shield-check',
  defaultOpen: true,
  class: showItem(user.value?.isAdmin()),
  children: [{
    label: 'Overview',
    to: '/home/admin',
    exact: true,
    class: showItem(user.value?.isAdmin()),
    onSelect: () => {
      open.value = false
    }
  }, {
    label: 'Users',
    to: '/home/admin/users',
    class: showItem(user.value?.isAdmin()),
    onSelect: () => {
      open.value = false
    }
  }]
}, {
  label: 'Settings',
  to: '/home/settings',
  icon: 'i-lucide-settings',
  defaultOpen: true,
  children: [{
    label: 'General',
    to: '/home/settings',
    exact: true,
    onSelect: () => {
      open.value = false
    }
  }, {
    label: 'Notifications',
    to: '/home/settings/notifications',
    onSelect: () => {
      open.value = false
    }
  }, {
    label: 'Security',
    to: '/home/settings/security',
    onSelect: () => {
      open.value = false
    }
  }]
}]
const groups = computed(() => [{
  id: 'links',
  label: 'Go to',
  items: links.flat()
}])

onBeforeMount(async () => {
  if (!getToken()) {
    // User is not logged in
      toast.add({
        title: 'Ups...',
        description: 'Please log in to access the dashboard',
        color: 'error'
      })
    navigateTo('/login')
  }
})
</script>

<template>
  <UDashboardGroup unit="rem">
    <UDashboardSidebar
      id="default"
      v-model:open="open"
      collapsible
      resizable
      class="bg-(--ui-bg-elevated)/25"
      :ui="{ footer: 'lg:border-t lg:border-(--ui-border)' }"
    >
      <template #header="{ collapsed }">
        <div v-if="collapsed" class="font-bold flex flex-col">
          Rent<span class="text-primary-500">Ease</span>
        </div>
        <div v-if="!collapsed" class="w-auto font-bold text-2xl">
          Rent<span class="text-primary-500">Ease</span>
        </div>
      </template>



      <template #default="{ collapsed }">
        <UDashboardSearchButton :collapsed="collapsed" class="bg-transparent ring-(--ui-border)" />

        <UNavigationMenu
          :collapsed="collapsed"
          :items="links"
          orientation="vertical"
          tooltip
        />

      </template>

      <template #footer="{ collapsed }">
        <UserMenu :collapsed="collapsed" />
      </template>
    </UDashboardSidebar>

    <UDashboardSearch :groups="groups" />

    <slot />

    <NotificationsSlideover />
  </UDashboardGroup>
</template>
