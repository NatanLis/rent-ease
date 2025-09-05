<!-- components/InboxMail.vue -->
<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue';
import type { Mail, Message } from '~/types';

const props = defineProps<{ mail: Mail }>();
const emit = defineEmits<{ (e: 'close'): void; (e: 'deleted'): void }>();

const messages = ref<Message[]>(props.mail?.messages ?? []);
const replyText = ref('');
const sending = ref(false);
const scroller = ref<HTMLElement | null>(null);
let pollTimer: number | null = null;
let es: EventSource | null = null;

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

function startSSE() {
  try {
    if (es) es.close();
    es = new EventSource(`/api/chat/stream?threadId=${encodeURIComponent(String(props.mail.id))}`);
    es.addEventListener('message', (evt: MessageEvent) => {
      try {
        const data = JSON.parse(evt.data) as Message;
        // only push if it's for this thread and not duplicate
        if (!messages.value.find(m => m.id === (data as any).id)) {
          messages.value.push(data);
        }
      } catch (_) {}
    });
  } catch (e) {
    console.error('SSE connection failed', e);
  }
}

onMounted(() => {
  startSSE();
});

onBeforeUnmount(() => {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
  if (es) { es.close(); es = null; }
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
    // optimistic add
    const optimistic: Message = {
      id: `local-${Date.now()}`,
      from: 'agent@noreply',
      to,
      text,
      date: new Date().toISOString(),
      isOutgoing: true,
      subject: `Re: ${props.mail.subject || ''}`
    }
    messages.value.push(optimistic);

    await $fetch('/api/chat/messages', {
      method: 'POST',
      body: {
        threadId: props.mail.id,
        text,
        senderEmail: 'agent@noreply',
        recipientEmail: to,
        subject: `Re: ${props.mail.subject || ''}`
      }
    });
    replyText.value = '';
  } catch (e) {
    console.error('Send failed', e);
    alert('Failed to send.');
  } finally {
    sending.value = false;
    scrollToBottom();
  }
}

async function deleteChat() {
  if (!confirm('Are you sure you want to delete this chat? This action cannot be undone.')) {
    return
  }
  
  try {
    await $fetch(`/api/chat/${props.mail.id}`, { method: 'DELETE' })
    emit('deleted')
    emit('close')
  } catch (e) {
    console.error('Failed to delete chat', e)
    alert('Failed to delete chat')
  }
}
</script>

<template>
  <div class="flex flex-col h-full flex-1 w-full border border-(--ui-border) rounded overflow-hidden bg-(--ui-bg)">
    <!-- Header -->
    <div class="px-4 py-3 border-b border-(--ui-border) flex items-center justify-between bg-(--ui-bg-elevated)">
      <div>
        <div class="font-semibold">
          {{ props.mail.to?.name || props.mail.to?.email || props.mail.subject || 'Conversation' }}
        </div>
        <div v-if="props.mail.to?.email" class="text-xs text-(--ui-text-dimmed)">
          {{ props.mail.to.email }}
        </div>
      </div>
      <div class="flex gap-2">
        <UButton color="primary" icon="i-lucide-trash-2" @click="deleteChat">
          Delete
        </UButton>
        <UButton color="primary" icon="i-lucide-x" @click="$emit('close')">
          Close
        </UButton>
      </div>
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
        placeholder="Type a message..."
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
