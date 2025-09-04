<!-- components/InboxMail.vue -->
<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue';
import type { Mail, Message } from '~/types';

const props = defineProps<{ mail: Mail }>();
const emit = defineEmits<{ (e: 'close'): void }>();

const messages = ref<Message[]>(props.mail?.messages ?? []);
const replyText = ref('');
const sending = ref(false);
const scroller = ref<HTMLElement | null>(null);
let pollTimer: number | null = null;

watch(() => props.mail, (m) => {
  messages.value = m?.messages ?? [];
}, { immediate: true, deep: true });

function scrollToBottom() {
  nextTick(() => {
    if (scroller.value) scroller.value.scrollTop = scroller.value.scrollHeight;
  });
}
onMounted(scrollToBottom);
watch(messages, scrollToBottom, { deep: true });

async function refreshThread() {
  try {
    const all = await $fetch<Mail[]>('/api/mails');
    const latest = all.find(m => m.id === props.mail.id);
    if (latest?.messages) {
      messages.value = latest.messages as Message[];
    }
  } catch (e) {
    console.error('Polling inbox failed', e);
  }
}

onMounted(() => {
  pollTimer = window.setInterval(refreshThread, 3000);
});

onBeforeUnmount(() => {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
});

function getReplyTo(): string {
  const list = messages.value;
  if (list && list.length) {
    const last = list[list.length - 1];
    // Reply to the other party of the last message
    return last.isOutgoing ? (last.to || '') : (last.from || '');
  }
  // Fallback: top-level 'from' is typically the other participant
  if (props.mail.from?.email) return props.mail.from.email;
  if (props.mail.participants?.length) return props.mail.participants[0];
  return '';
}

async function sendReply() {
  const text = replyText.value.trim();
  if (!text) return;

  const to = getReplyTo();
  if (!to) {
    alert('No reply recipient found for this thread.');
    return;
  }

  sending.value = true;
  try {
    const res = await $fetch('/api/send-mail', {
      method: 'POST',
      body: {
        to,
        subject: `Re: ${props.mail.subject || ''}`,
        text,
        mailId: props.mail.id
      }
    });

    if (res?.message) {
      messages.value.push(res.message as Message);
    } else {
      // optimistic fallback
      messages.value.push({
        id: `local-${Date.now()}`,
        from: 'noreply',
        to,
        text,
        date: new Date().toISOString(),
        isOutgoing: true,
        subject: `Re: ${props.mail.subject || ''}`
      });
    }
    replyText.value = '';
  } catch (e) {
    console.error('Send failed', e);
    alert('Failed to send. Check server logs and .env credentials.');
  } finally {
    sending.value = false;
    scrollToBottom();
  }
}
</script>

<template>
  <div class="flex flex-col h-full flex-1 w-full border border-(--ui-border) rounded overflow-hidden bg-(--ui-bg)">
    <!-- Header -->
    <div class="px-4 py-3 border-b border-(--ui-border) flex items-center justify-between bg-(--ui-bg-elevated)">
      <div>
        <div class="font-semibold">{{ props.mail.subject }}</div>
        <div class="text-xs text-gray-500">
          <!-- Safe to read because we provided defaults in the data -->
          <template v-if="props.mail.from">
            From: {{ props.mail.from.name }} &lt;{{ props.mail.from.email }}&gt;
          </template>
        </div>
      </div>
      <UButton color="primary" icon="i-lucide-x" @click="$emit('close')">
        Close
      </UButton>
    </div>

    <!-- Messages -->
    <div ref="scroller" class="flex-1 overflow-y-auto p-4 space-y-3 bg-(--ui-bg)">
      <div v-for="m in messages" :key="m.id" class="flex">
        <div
          :class="[
            'max-w-[70%] px-3 py-2 rounded-xl border break-words whitespace-pre-wrap text-sm',
            m.isOutgoing
              ? 'ml-auto bg-(--ui-primary)/10 border-(--ui-primary)/30 text-right text-(--ui-text)'
              : 'mr-auto bg-(--ui-bg-elevated) border-(--ui-border) text-left text-(--ui-text)'
          ]"
        >
          <div class="leading-relaxed">{{ m.text }}</div>
          <div class="text-xs text-(--ui-text-dimmed) mt-1">{{ new Date(m.date).toLocaleString() }}</div>
        </div>
      </div>
    </div>

    <!-- Composer -->
    <form @submit.prevent="sendReply" class="border-t border-(--ui-border) px-3 py-3 flex gap-2 items-end bg-(--ui-bg-elevated)">
      <UTextarea
        v-model="replyText"
        placeholder="Type a reply..."
        :rows="2"
        autoresize
        class="flex-1"
      />
      <UButton type="submit" :loading="sending" :disabled="!replyText.trim()" icon="i-lucide-send" color="primary">
        Send
      </UButton>
    </form>
  </div>
</template>
