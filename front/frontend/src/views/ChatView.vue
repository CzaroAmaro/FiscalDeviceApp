<template>
  <v-card class="d-flex flex-column" style="height: 100vh; max-height: calc(100vh - 80px);">

    <v-toolbar flat>
      <v-toolbar-title>Czat Firmowy</v-toolbar-title>
      <v-spacer />
      <v-chip :color="statusColor" variant="elevated">
        <v-progress-circular v-if="chatStore.status === 'connecting'" indeterminate size="16" class="mr-2" />
        {{ chatStore.status }}
      </v-chip>
    </v-toolbar>

    <v-divider />

    <v-card-text ref="messageContainer" class="flex-grow-1 overflow-y-auto" @scroll="handleScroll">
      <div class="text-center py-2">
        <v-btn
          v-if="chatStore.nextHistoryUrl"
          :loading="chatStore.isLoadingHistory"
          size="small"
          variant="tonal"
          @click="chatStore.fetchHistory"
        >
          Wczytaj starsze
        </v-btn>
      </div>
      <div v-for="msg in chatStore.messages" :key="msg.id" class="my-4" :class="isMyMessage(msg) ? 'd-flex justify-end' : 'd-flex justify-start'">
        <v-chip :color="isMyMessage(msg) ? 'primary' : ''" class="pa-3" style="height: auto; white-space: normal; max-width: 70%;">
          <div>
            <div v-if="!isMyMessage(msg)" class="font-weight-bold">{{ msg.sender_name }}</div>
            <p class="mb-0">{{ msg.content }}</p>
            <div class="text-caption text-right mt-1" :style="{ color: isMyMessage(msg) ? 'rgba(255,255,255,0.7)' : '' }">{{ formatTimestamp(msg.timestamp) }}</div>
          </div>
        </v-chip>
      </div>
    </v-card-text>

    <v-divider />

    <v-card-actions class="pa-4">
      <v-text-field
        v-model="newMessage"
        label="Napisz wiadomość..."
        variant="solo"
        hide-details
        append-inner-icon="mdi-send"
        :disabled="chatStore.status !== 'open'"
        @click:append-inner="handleSendMessage"
        @keydown.enter.prevent="handleSendMessage"
      />
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, nextTick, watch } from 'vue';
import { useChatStore } from '@/stores/chat';
import { useAuthStore } from '@/stores/auth';
import { format, isToday, isYesterday } from 'date-fns';
import { pl } from 'date-fns/locale';
import type { Message } from '@/types';

const chatStore = useChatStore();
const authStore = useAuthStore();

const newMessage = ref('');
const messageContainer = ref<HTMLElement | null>(null);

const myId = computed(() => authStore.user?.technician_profile?.id);

const isMyMessage = (msg: Message) => msg.sender_id === myId.value;

const statusColor = computed(() => {
  switch (chatStore.status) {
    case 'open': return 'success';
    case 'connecting': return 'warning';
    default: return 'error';
  }
});

function handleSendMessage() {
  if (newMessage.value.trim() && chatStore.status === 'open') {
    chatStore.sendMessage(newMessage.value);
    newMessage.value = '';
    scrollToBottom();
  }
}

function scrollToBottom(behavior: 'auto' | 'smooth' = 'auto') { // <<< ZMIANA 1: Jawny, prosty typ
  nextTick(() => {
    if (messageContainer.value) {
      messageContainer.value.scrollTo({
        top: messageContainer.value.scrollHeight,
        behavior: behavior,
      });
    }
  });
}

function handleScroll(e: Event) {
  const target = e.target as HTMLElement;
  const oldScrollHeight = target.scrollHeight;

  if (target.scrollTop === 0 && chatStore.nextHistoryUrl && !chatStore.isLoadingHistory) {
    chatStore.fetchHistory().then(() => {
      nextTick(() => {
        if (messageContainer.value) {
          messageContainer.value.scrollTop = messageContainer.value.scrollHeight - oldScrollHeight;
        }
      });
    });
  }
}

// --- KONIEC POPRAWKI ---

watch(() => chatStore.messages.length, (newLength, oldLength) => {
  if (newLength > oldLength && oldLength > 0) {
    const container = messageContainer.value;
    if (container && container.scrollHeight - container.scrollTop <= container.clientHeight + 200) {
      scrollToBottom('smooth'); // Płynne przewinięcie dla nowych wiadomości
    }
  }
});

onMounted(async () => {
  chatStore.connect();
  await chatStore.fetchHistory();
  scrollToBottom(); // Używamy domyślnego 'auto' dla natychmiastowego przewinięcia
});

onUnmounted(() => {
  chatStore.disconnect();
  chatStore.clearChatState();
});

function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  if (isToday(date)) return format(date, 'HH:mm');
  if (isYesterday(date)) return `Wczoraj, ${format(date, 'HH:mm')}`;
  return format(date, 'dd.MM.yyyy, HH:mm', { locale: pl });
}
</script>

<style scoped>
p {
  word-break: break-word;
}
</style>
