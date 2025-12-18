<template>
  <v-container fluid class="chat-container pa-4">
    <v-card class="chat-card d-flex flex-column" rounded="lg" elevation="2">

      <!-- Nagłówek czatu -->
      <div class="chat-header pa-4">
        <div class="d-flex align-center justify-space-between">
          <div class="d-flex align-center">
            <v-avatar color="primary" size="42" class="mr-3">
              <v-icon>mdi-forum</v-icon>
            </v-avatar>
            <div>
              <h2 class="text-h6 font-weight-bold mb-0">Czat Firmowy</h2>
              <p class="text-caption text-medium-emphasis mb-0">
                {{ onlineInfo }}
              </p>
            </div>
          </div>

          <div class="d-flex align-center ga-2">
            <v-chip
              :color="statusColor"
              variant="tonal"
              size="small"
              class="status-chip"
            >
              <v-icon
                start
                size="12"
                :class="{ 'status-pulse': chatStore.status === 'open' }"
              >
                mdi-circle
              </v-icon>
              {{ statusText }}
            </v-chip>
          </div>
        </div>
      </div>

      <v-divider />

      <!-- Obszar wiadomości -->
      <div
        ref="messageContainer"
        class="messages-container flex-grow-1"
        @scroll="handleScroll"
      >
        <!-- Loader starszych wiadomości -->
        <div v-if="chatStore.nextHistoryUrl" class="text-center py-4">
          <v-btn
            :loading="chatStore.isLoadingHistory"
            size="small"
            variant="tonal"
            color="primary"
            rounded="pill"
            @click="chatStore.fetchHistory"
          >
            <v-icon start>mdi-history</v-icon>
            Wczytaj starsze wiadomości
          </v-btn>
        </div>

        <!-- Pusta lista -->
        <div
          v-if="chatStore.messages.length === 0 && !chatStore.isLoadingHistory"
          class="empty-state"
        >
          <v-icon size="80" color="grey-lighten-2" class="mb-4">
            mdi-chat-outline
          </v-icon>
          <h3 class="text-h6 text-grey-darken-1 mb-2">Brak wiadomości</h3>
          <p class="text-body-2 text-grey">
            Rozpocznij rozmowę z zespołem
          </p>
        </div>

        <!-- Lista wiadomości -->
        <div class="messages-list pa-4">
          <template v-for="(msg, index) in chatStore.messages" :key="msg.id">
            <!-- Separator daty -->
            <div
              v-if="shouldShowDateSeparator(index)"
              class="date-separator my-4"
            >
              <span class="date-label">{{ getDateLabel(msg.timestamp) }}</span>
            </div>

            <!-- Wiadomość -->
            <div
              class="message-wrapper mb-3"
              :class="{
                'message-own': isMyMessage(msg),
                'message-other': !isMyMessage(msg)
              }"
            >
              <!-- Avatar (tylko dla innych) -->
              <v-avatar
                v-if="!isMyMessage(msg)"
                :color="getAvatarColor(msg.sender_id)"
                size="36"
                class="message-avatar"
              >
                <span class="text-caption font-weight-bold">
                  {{ getInitials(msg.sender_name) }}
                </span>
              </v-avatar>

              <div class="message-content">
                <!-- Nazwa nadawcy (tylko dla innych) -->
                <div v-if="!isMyMessage(msg)" class="sender-name text-caption font-weight-medium mb-1">
                  {{ msg.sender_name }}
                </div>

                <!-- Bąbelek wiadomości -->
                <div class="message-bubble">
                  <p class="message-text mb-0">{{ msg.content }}</p>
                  <div class="message-time">
                    {{ formatTime(msg.timestamp) }}
                    <v-icon
                      v-if="isMyMessage(msg)"
                      size="14"
                      class="ml-1"
                    >
                      mdi-check-all
                    </v-icon>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>

        <!-- Scroll to bottom button -->
        <v-scale-transition>
          <v-btn
            v-if="showScrollButton"
            icon
            color="primary"
            size="small"
            class="scroll-bottom-btn"
            elevation="4"
            @click="scrollToBottom('smooth')"
          >
            <v-icon>mdi-chevron-down</v-icon>
          </v-btn>
        </v-scale-transition>
      </div>

      <v-divider />

      <!-- Pole wprowadzania wiadomości -->
      <div class="message-input-container pa-4">
        <div class="d-flex align-center ga-3">

          <!-- Pole tekstowe -->
          <v-textarea
            v-model="newMessage"
            placeholder="Napisz wiadomość..."
            variant="outlined"
            density="compact"
            hide-details
            auto-grow
            rows="1"
            max-rows="4"
            :disabled="chatStore.status !== 'open'"
            class="message-input flex-grow-1"
            @keydown.enter.exact.prevent="handleSendMessage"
            @keydown.enter.shift.prevent="newMessage += '\n'"
          />

          <!-- Przycisk wysyłania -->
          <v-btn
            icon
            color="primary"
            :disabled="!canSend"
            :loading="isSending"
            @click="handleSendMessage"
          >
            <v-icon>mdi-send</v-icon>
            <v-tooltip activator="parent" location="top">
              Wyślij (Enter)
            </v-tooltip>
          </v-btn>
        </div>

        <!-- Wskazówka -->
        <p class="text-caption text-medium-emphasis mt-2 mb-0">
          <kbd>Enter</kbd> wysyła • <kbd>Shift + Enter</kbd> nowa linia
        </p>
      </div>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, nextTick, watch } from 'vue';
import { useChatStore } from '@/stores/chat';
import { useAuthStore } from '@/stores/auth';
import { format, isToday, isYesterday, isSameDay } from 'date-fns';
import { pl } from 'date-fns/locale';
import type { Message } from '@/types';

const chatStore = useChatStore();
const authStore = useAuthStore();

const newMessage = ref('');
const messageContainer = ref<HTMLElement | null>(null);
const showScrollButton = ref(false);
const isSending = ref(false);

const myId = computed(() => authStore.user?.technician_profile?.id);

const isMyMessage = (msg: Message) => msg.sender_id === myId.value;

const canSend = computed(() => {
  return newMessage.value.trim().length > 0 && chatStore.status === 'open';
});

const statusColor = computed(() => {
  switch (chatStore.status) {
    case 'open': return 'success';
    case 'connecting': return 'warning';
    default: return 'error';
  }
});

const statusText = computed(() => {
  switch (chatStore.status) {
    case 'open': return 'Połączono';
    case 'connecting': return 'Łączenie...';
    default: return 'Rozłączono';
  }
});

const onlineInfo = computed(() => {
  // Możesz tu dodać liczbę online użytkowników
  return 'Komunikacja zespołowa w czasie rzeczywistym';
});

// Kolory avatarów bazowane na ID
const avatarColors = ['primary', 'secondary', 'success', 'warning', 'info', 'error'];
const getAvatarColor = (senderId: number) => {
  return avatarColors[senderId % avatarColors.length];
};

// Inicjały z imienia
const getInitials = (name: string) => {
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
};

// Separator daty
const shouldShowDateSeparator = (index: number) => {
  if (index === 0) return true;
  const currentMsg = chatStore.messages[index];
  const prevMsg = chatStore.messages[index - 1];
  return !isSameDay(new Date(currentMsg.timestamp), new Date(prevMsg.timestamp));
};

const getDateLabel = (timestamp: string) => {
  const date = new Date(timestamp);
  if (isToday(date)) return 'Dzisiaj';
  if (isYesterday(date)) return 'Wczoraj';
  return format(date, 'd MMMM yyyy', { locale: pl });
};

const formatTime = (timestamp: string) => {
  return format(new Date(timestamp), 'HH:mm');
};

async function handleSendMessage() {
  if (!canSend.value) return;

  const message = newMessage.value.trim();
  newMessage.value = '';
  isSending.value = true;

  try {
    chatStore.sendMessage(message);
    scrollToBottom('smooth');
  } finally {
    isSending.value = false;
  }
}

function scrollToBottom(behavior: 'auto' | 'smooth' = 'auto') {
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

  // Pokaż przycisk scroll to bottom
  const distanceFromBottom = target.scrollHeight - target.scrollTop - target.clientHeight;
  showScrollButton.value = distanceFromBottom > 300;

  // Wczytaj starsze wiadomości
  if (target.scrollTop < 100 && chatStore.nextHistoryUrl && !chatStore.isLoadingHistory) {
    chatStore.fetchHistory().then(() => {
      nextTick(() => {
        if (messageContainer.value) {
          messageContainer.value.scrollTop = messageContainer.value.scrollHeight - oldScrollHeight;
        }
      });
    });
  }
}

watch(() => chatStore.messages.length, (newLength, oldLength) => {
  if (newLength > oldLength && oldLength > 0) {
    const container = messageContainer.value;
    if (container && container.scrollHeight - container.scrollTop <= container.clientHeight + 200) {
      scrollToBottom('smooth');
    }
  }
});

onMounted(async () => {
  chatStore.connect();
  await chatStore.fetchHistory();
  scrollToBottom();
});

onUnmounted(() => {
  chatStore.disconnect();
  chatStore.clearChatState();
});
</script>

<style scoped>
.chat-container {
  height: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.chat-card {
  height: calc(100vh - 100px);
  max-height: 900px;
  min-height: 500px;
}

/* ===== NAGŁÓWEK ===== */
.chat-header {
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-primary), 0.05) 0%,
    rgba(var(--v-theme-primary), 0.02) 100%
  );
}

.status-chip {
  font-size: 0.75rem;
}

.status-pulse {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* ===== OBSZAR WIADOMOŚCI ===== */
.messages-container {
  position: relative;
  overflow-y: auto;
  background: linear-gradient(
    180deg,
    rgba(var(--v-theme-surface), 1) 0%,
    rgba(var(--v-theme-background), 0.5) 100%
  );
}

.messages-list {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 48px;
  text-align: center;
}

/* ===== SEPARATOR DATY ===== */
.date-separator {
  display: flex;
  align-items: center;
  justify-content: center;
}

.date-label {
  background: rgba(var(--v-theme-on-surface), 0.08);
  padding: 4px 16px;
  border-radius: 12px;
  font-size: 0.75rem;
  color: rgba(var(--v-theme-on-surface), 0.6);
  font-weight: 500;
}

/* ===== WIADOMOŚCI ===== */
.message-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  max-width: 75%;
}

.message-own {
  margin-left: auto;
  flex-direction: row-reverse;
}

.message-other {
  margin-right: auto;
}

.message-avatar {
  flex-shrink: 0;
  margin-bottom: 4px;
}

.message-content {
  display: flex;
  flex-direction: column;
}

.message-own .message-content {
  align-items: flex-end;
}

.sender-name {
  color: rgba(var(--v-theme-on-surface), 0.7);
  margin-left: 12px;
}

.message-bubble {
  padding: 10px 14px;
  border-radius: 18px;
  max-width: 100%;
  word-wrap: break-word;
}

.message-own .message-bubble {
  background: rgb(var(--v-theme-primary));
  color: white;
  border-bottom-right-radius: 4px;
}

.message-other .message-bubble {
  background: rgba(var(--v-theme-on-surface), 0.08);
  border-bottom-left-radius: 4px;
}

.message-text {
  font-size: 0.9375rem;
  line-height: 1.4;
  white-space: pre-wrap;
}

.message-time {
  font-size: 0.6875rem;
  opacity: 0.7;
  margin-top: 4px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.message-own .message-time {
  color: rgba(255, 255, 255, 0.8);
}

/* ===== SCROLL BUTTON ===== */
.scroll-bottom-btn {
  position: absolute;
  bottom: 16px;
  right: 16px;
}

/* ===== INPUT ===== */
.message-input-container {
  background: rgb(var(--v-theme-surface));
}

.message-input :deep(.v-field) {
  border-radius: 24px;
}

.message-input :deep(textarea) {
  padding: 8px 0;
  padding-left: 20px;
}

kbd {
  background: rgba(var(--v-theme-on-surface), 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-family: inherit;
}

/* ===== SCROLLBAR ===== */
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: transparent;
}

.messages-container::-webkit-scrollbar-thumb {
  background: rgba(var(--v-theme-on-surface), 0.2);
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--v-theme-on-surface), 0.3);
}

/* ===== RESPONSYWNOŚĆ ===== */
@media (max-width: 600px) {
  .chat-container {
    padding: 0;
  }

  .chat-card {
    height: 100vh;
    max-height: none;
    border-radius: 0;
  }

  .message-wrapper {
    max-width: 85%;
  }
}
</style>
