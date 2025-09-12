<script setup lang="ts">
import * as z from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'

const fileRef = ref<HTMLInputElement>()
const isUploading = ref(false)
const isLoading = ref(false)

const profileSchema = z.object({
  first_name: z.string().min(2, 'Too short'),
  last_name: z.string().min(2, 'Too short'),
  email: z.string().email('Invalid email'),
  username: z.string().min(2, 'Too short'),
  avatar: z.string().optional(),
  bio: z.string().optional()
})

type ProfileSchema = z.output<typeof profileSchema>

const profile = reactive<Partial<ProfileSchema>>({
  first_name: '',
  last_name: '',
  email: '',
  username: '',
  avatar: undefined,
  bio: undefined
})

const toast = useToast()
const { getUser, updateUser } = useUser()
const { getToken } = useAuth()

// Load current user data
onMounted(async () => {
  const currentUser = getUser()
  if (currentUser) {
    profile.first_name = currentUser.first_name
    profile.last_name = currentUser.last_name
    profile.email = currentUser.email
    profile.username = currentUser.username
    profile.avatar = currentUser.avatar_url || undefined
    profile.bio = ''
  }
})

async function onSubmit(event: FormSubmitEvent<ProfileSchema>) {
  if (isLoading.value) return

  isLoading.value = true

  try {
    const token = getToken()
    if (!token) {
      throw new Error('No authentication token found')
    }

    // Send profile data to backend
    const response = await $fetch('/api/auth/me', {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: {
        first_name: event.data.first_name,
        last_name: event.data.last_name,
        email: event.data.email,
        username: event.data.username
      }
    })

    if (response) {
      // Update local user data
      updateUser({
        first_name: response.first_name,
        last_name: response.last_name,
        email: response.email,
        username: response.username
      })

      toast.add({
        title: 'Success',
        description: 'Your profile has been updated.',
        icon: 'i-lucide-check',
        color: 'success'
      })
    }
  } catch (error: any) {
    console.error('Profile update error:', error)
    toast.add({
      title: 'Error',
      description: error.data?.message || 'Failed to update profile.',
      icon: 'i-lucide-x',
      color: 'red'
    })
  } finally {
    isLoading.value = false
  }
}

async function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement

  if (!input.files?.length) {
    return
  }

  const file = input.files[0]

  // Validate file type
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
  if (!allowedTypes.includes(file.type)) {
    toast.add({
      title: 'Invalid file type',
      description: 'Only JPG, PNG, and GIF files are allowed.',
      icon: 'i-lucide-x',
      color: 'red'
    })
    return
  }

  // Validate file size (1MB max)
  const maxSize = 1024 * 1024 // 1MB
  if (file.size > maxSize) {
    toast.add({
      title: 'File too large',
      description: 'Maximum file size is 1MB.',
      icon: 'i-lucide-x',
      color: 'red'
    })
    return
  }

  isUploading.value = true

  try {
    const currentUser = getUser()
    if (!currentUser) {
      throw new Error('User not authenticated')
    }

    // Create FormData for upload
    const formData = new FormData()
    formData.append('file', file)

    // Upload to backend
    const response = await $fetch('/api/profile-pictures/upload', {
      method: 'POST',
      body: formData,
      headers: {
        'X-User-ID': currentUser.id.toString()
      }
    })

    if (response.success) {
      // Update profile with new avatar URL
      profile.avatar = response.profilePicture.url

      // Update user data
      updateUser({
        avatar_url: response.profilePicture.url,
        profile_picture_id: response.profilePicture.id
      })

      toast.add({
        title: 'Success',
        description: 'Profile picture uploaded successfully.',
        icon: 'i-lucide-check',
        color: 'success'
      })
    }
  } catch (error) {
    console.error('Upload error:', error)
    toast.add({
      title: 'Upload failed',
      description: 'Failed to upload profile picture. Please try again.',
      icon: 'i-lucide-x',
      color: 'red'
    })
  } finally {
    isUploading.value = false
    // Clear the input
    if (input) {
      input.value = ''
    }
  }
}

function onFileClick() {
  fileRef.value?.click()
}

definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})
</script>

<template>
  <UForm
    id="settings"
    :schema="profileSchema"
    :state="profile"
    @submit="onSubmit"
  >
    <UPageCard
      title="Profile"
      description="These informations will be displayed publicly."
      variant="naked"
      orientation="horizontal"
      class="mb-4"
    >
      <UButton
        form="settings"
        label="Save changes"
        color="neutral"
        type="submit"
        class="w-fit lg:ms-auto"
        :loading="isLoading"
        :disabled="isLoading"
      />
    </UPageCard>

    <UPageCard variant="subtle">
      <UFormField
        name="first_name"
        label="First Name"
        description="Your first name."
        required
        class="flex max-sm:flex-col justify-between items-start gap-4"
      >
        <UInput
          v-model="profile.first_name"
          autocomplete="off"
        />
      </UFormField>
      <USeparator />
      <UFormField
        name="last_name"
        label="Last Name"
        description="Your last name."
        required
        class="flex max-sm:flex-col justify-between items-start gap-4"
      >
        <UInput
          v-model="profile.last_name"
          autocomplete="off"
        />
      </UFormField>
      <USeparator />
      <UFormField
        name="email"
        label="Email"
        description="Used to sign in, for email receipts and product updates."
        required
        class="flex max-sm:flex-col justify-between items-start gap-4"
      >
        <UInput
          v-model="profile.email"
          type="email"
          autocomplete="off"
        />
      </UFormField>
      <USeparator />
      <UFormField
        name="username"
        label="Username"
        description="Your unique username for logging in and your profile URL."
        required
        class="flex max-sm:flex-col justify-between items-start gap-4"
      >
        <UInput
          v-model="profile.username"
          type="username"
          autocomplete="off"
        />
      </UFormField>
      <USeparator />
      <UFormField
        name="avatar"
        label="Avatar"
        hidden=true
        description="JPG, GIF or PNG. 1MB Max."
        class="flex max-sm:flex-col justify-between sm:items-center gap-4"
      >
        <div class="flex flex-wrap items-center gap-3">
          <UAvatar
            :src="profile.avatar"
            :alt="`${profile.first_name} ${profile.last_name}`"
            size="lg"
          />
          <UButton
            :label="isUploading ? 'Uploading...' : 'Choose'"
            :loading="isUploading"
            :disabled="isUploading"
            color="neutral"
            @click="onFileClick"
          />
          <input
            ref="fileRef"
            type="file"
            class="hidden"
            accept=".jpg, .jpeg, .png, .gif"
            :disabled="isUploading"
            @change="onFileChange"
          >
        </div>
      </UFormField>
      <!-- <USeparator /> -->
      <UFormField
        name="bio"
        label="Bio"
        description="Brief description for your profile. URLs are hyperlinked."
        class="flex max-sm:flex-col justify-between items-start gap-4"
        :ui="{ container: 'w-full' }"
      >
        <UTextarea
          v-model="profile.bio"
          :rows="5"
          autoresize
          class="w-full"
        />
      </UFormField>
    </UPageCard>
  </UForm>
</template>
