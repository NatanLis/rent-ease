<script setup lang="ts">
import * as z from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'

const toast = useToast()
const { setToken, getToken } = useAuth()
const { setUser } = useUser()
const fields = [{
  name: 'email',
  type: 'text' as const,
  label: 'Email',
  placeholder: 'Enter your email',
  required: true
}, {
  name: 'password',
  label: 'Password',
  type: 'password' as const,
  placeholder: 'Enter your password'
}, {
  name: 'remember',
  label: 'Remember me',
  type: 'checkbox' as const
}]

const providers = [{
  label: 'Google',
  icon: 'i-simple-icons-google',
  onClick: () => {
    toast.add({ title: 'Google', description: 'Login with Google' })
  }
},
// {
//   label: 'GitHub',
//   icon: 'i-simple-icons-github',
//   onClick: () => {
//     toast.add({ title: 'GitHub', description: 'Login with GitHub' })
//   }
// }
]

const schema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Must be at least 8 characters')
})

type Schema = z.output<typeof schema>

async function onSubmit(payload: FormSubmitEvent<Schema>) {
  const res = await logIn(payload.data.email, payload.data.password)
  if (res?.token.access_token) {
    setToken(res.token.access_token)
    setUser(res.user)
    navigateTo('/home')
  }
}

async function logIn(username: string, password: string) {
  try {
    const params = new URLSearchParams({
      grant_type: 'password',
      username,
      password,
      scope: '',
      client_id: 'string',
      client_secret: '********'
    })
    const response = await fetch('http://localhost:8000/auth/login', {
      method: 'POST',
      headers: {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: params.toString()
    })
    if (!response.ok) {
      throw new Error('Failed to sign up')
    }
    const data = await response.json()
    toast.add({ title: 'Success', description: 'Signed up successfully!' })
    return data
  } catch (error: any) {
    toast.add({ title: 'Error', description: error.message })
    return null
  }
}

onBeforeMount(() => {
  if (getToken()) {
    // User is already logged in
    navigateTo('/home')
  }
})

definePageMeta({
  layout: 'landing'
})
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-4 p-4">
    <UPageCard class="w-full max-w-md">
      <UAuthForm
        :schema="schema"
        title="Login"
        description="Enter your credentials to access your account."
        icon="i-lucide-user"
        :fields="fields"
        :providers="providers"
        @submit="onSubmit"
      />
    </UPageCard>
  </div>
</template>

