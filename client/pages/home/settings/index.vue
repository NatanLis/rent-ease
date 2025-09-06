<script setup lang="ts">
import * as z from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'

const fileRef = ref<HTMLInputElement>()
const isUploading = ref(false)

const profileSchema = z.object({
  name: z.string().min(2, 'Too short'),
  email: z.string().email('Invalid email'),
  username: z.string().min(2, 'Too short'),
  avatar: z.string().optional(),
  bio: z.string().optional()
})

type ProfileSchema = z.output<typeof profileSchema>

const profile = reactive<Partial<ProfileSchema>>({
  name: 'Benjamin Canac',
  email: 'ben@nuxtlabs.com',
  username: 'benjamincanac',
  avatar: undefined,
  bio: undefined
})

const toast = useToast()

async function onSubmit(event: FormSubmitEvent<ProfileSchema>) {
  try {
    // Here you would send the profile data to your backend
    // For now, just show success message
    toast.add({
      title: 'Success',
      description: 'Your settings have been updated.',
      icon: 'i-lucide-check',
      color: 'success'
    })
    console.log(event.data)
  } catch (error) {
    toast.add({
      title: 'Error',
      description: 'Failed to update settings.',
      icon: 'i-lucide-x',
      color: 'red'
    })
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
    // Create FormData for upload
    const formData = new FormData()
    formData.append('file', file)

    // Upload to backend
    const response = await $fetch('/api/profile-pictures/upload', {
      method: 'POST',
      body: formData,
      headers: {
        'X-User-ID': '1' // TODO: Get from auth context
      }
    })

    if (response.success) {
      // Update profile with new avatar URL
      profile.avatar = response.profilePicture.url
      
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
      />
    </UPageCard>

    <UPageCard variant="subtle">
      <UFormField
        name="name"
        label="Name"
        description="Will appear on receipts, invoices, and other communication."
        required
        class="flex max-sm:flex-col justify-between items-start gap-4"
      >
        <UInput
          v-model="profile.name"
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
        description="JPG, GIF or PNG. 1MB Max."
        class="flex max-sm:flex-col justify-between sm:items-center gap-4"
      >
        <div class="flex flex-wrap items-center gap-3">
          <UAvatar
            :src="profile.avatar"
            :alt="profile.name"
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
      <USeparator />
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
