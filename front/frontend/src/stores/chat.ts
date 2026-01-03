import { defineStore } from 'pinia';

import { fetchMessageHistory } from '@/api/chat';
import { useAuthStore } from '@/stores/auth.ts';
import type { Message } from '@/types';

interface ChatState {
  socket: WebSocket | null;
  status: 'connecting' | 'open' | 'closing' | 'closed';
  messages: Message[];
  nextHistoryUrl: string | null;
  isLoadingHistory: boolean;
}

const INITIAL_HISTORY_URL = '/messages/?limit=20';

export const useChatStore = defineStore('chat', {
  state: (): ChatState => ({
    socket: null,
    status: 'closed',
    messages: [],
    nextHistoryUrl: INITIAL_HISTORY_URL,
    isLoadingHistory: false,
  }),

  actions: {
    async fetchHistory() {
      if (!this.nextHistoryUrl || this.isLoadingHistory) return;

      this.isLoadingHistory = true;
      try {
        const response = await fetchMessageHistory(this.nextHistoryUrl);

        if (response && Array.isArray(response.results)) {
          this.messages.unshift(...response.results.reverse());
          this.nextHistoryUrl = response.next;
        } else {
          this.nextHistoryUrl = null;
          console.warn("Received invalid response from message history API.");
        }
      } catch (error) {
        console.error('Failed to fetch message history:', error);
      } finally {
        this.isLoadingHistory = false;
      }
    },

    connect() {
      if (this.socket && this.status === 'open') return;

      this.clearChatState();

      const authStore = useAuthStore();
      const token = authStore.accessToken;

      if (!token) {
        console.error("Cannot connect WS: no token");
        return;
      }

      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      const host = window.location.host;
      const url = `${protocol}://${host}/ws/chat/?token=${encodeURIComponent(token)}`;
      this.socket = new WebSocket(url);
      this.status = "connecting";

      this.socket.onopen = () => {
        this.status = "open";
      };

      this.socket.onmessage = (event) => {
        try {
          const newMessage: Message = JSON.parse(event.data);
          if (newMessage && newMessage.id) {
            this.messages.push(newMessage);
          }
        } catch (error) {
          console.error('Failed to parse incoming message:', error);
        }
      };

      this.socket.onclose = () => {
        this.status = 'closed';
        this.socket = null;
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.status = 'closed';
        this.socket = null;
      };
    },

    sendMessage(messageContent: string) {
      if (this.socket && this.status === 'open') {
        this.socket.send(JSON.stringify({ message: messageContent }));
      } else {
        console.error('Cannot send message, WebSocket is not open.');
      }
    },

    disconnect() {
      if (this.socket) {
        this.socket.close();
      }
    },

    clearChatState() {
      this.messages = [];
      this.nextHistoryUrl = INITIAL_HISTORY_URL;
      this.isLoadingHistory = false;
    }
  },
});
