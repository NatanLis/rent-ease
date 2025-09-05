<!-- <template>
  <div>
    <NuxtLoadingIndicator />
    <slot />
  </div>
</template>

<script lang="ts" setup>
</script> -->

<script setup lang="ts">
const route = useRoute()
const toast = useToast()
const { getToken } = useAuth()

const open = ref(false)

const links = [[{
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
  label: 'Customers',
  icon: 'i-lucide-users',
  to: '/home/customers',
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
  onSelect: () => {
    open.value = false
  }
}, {
  label: 'Leases',
  icon: 'i-lucide-file-text',
  to: '/home/leases',
  onSelect: () => {
    open.value = false
  }
}, {
  label: 'Properties',
  icon: 'i-lucide-building',
  to: '/home/properties',
  onSelect: () => {
    open.value = false
  }
}, {
  label: 'Units',
  icon: 'i-lucide-home',
  to: '/home/units',
  onSelect: () => {
    open.value = false
  }
}, {
  label: 'Admin Panel',
  to: '/home/admin',
  icon: 'i-lucide-shield-check',
  defaultOpen: true,
  children: [{
    label: 'Overview',
    to: '/home/admin',
    exact: true,
    onSelect: () => {
      open.value = false
    }
  }, {
    label: 'Users',
    to: '/home/admin/users',
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
    label: 'Members',
    to: '/home/settings/members',
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
}],
// [{
//   label: 'Feedback',
//   icon: 'i-lucide-message-circle',
//   to: 'https://github.com/nuxt-ui-pro/dashboard',
//   target: '_blank'
// }, {
//   label: 'Help & Support',
//   icon: 'i-lucide-info',
//   to: 'https://github.com/nuxt/ui-pro',
//   target: '_blank'
// }]
]

const groups = computed(() => [{
  id: 'links',
  label: 'Go to',
  items: links.flat()
}, {
  id: 'code',
  label: 'Code',
  items: [{
    id: 'source',
    label: 'View page source',
    icon: 'i-simple-icons-github',
    to: `https://github.com/nuxt-ui-pro/dashboard/blob/main/app/pages${route.path === '/' ? '/index' : route.path}.vue`,
    target: '_blank'
  }]
}])

onBeforeMount(async () => {
  // const cookie = useCookie('cookie-consent')
  // if (cookie.value === 'accepted') {
  //   return
  // }

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
      <!-- <template #header="{ collapsed }">
        <TeamsMenu :collapsed="collapsed" />
      </template> -->
      <template #header="{ collapsed }">
        <!-- <TeamsMenu :collapsed="collapsed" /> -->

        <div v-if="collapsed" class="font-bold">
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
          :items="links[0]"
          orientation="vertical"
        />

        <UNavigationMenu
          :collapsed="collapsed"
          :items="links[1]"
          orientation="vertical"
          class="mt-auto"
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
