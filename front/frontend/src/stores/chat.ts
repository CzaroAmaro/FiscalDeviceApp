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

// Definiujemy początkowy URL jako stałą, żeby łatwiej go resetować
const INITIAL_HISTORY_URL = '/messages/?limit=20'; // Zwiększyłem limit, żeby od razu było co scrollować

export const useChatStore = defineStore('chat', {
  state: (): ChatState => ({
    socket: null,
    status: 'closed',
    messages: [],
    nextHistoryUrl: INITIAL_HISTORY_URL,
    isLoadingHistory: false,
  }),

  actions: {
    // --- POCZĄTEK ZMIAN w fetchHistory ---
    async fetchHistory() {
      if (!this.nextHistoryUrl || this.isLoadingHistory) return;

      this.isLoadingHistory = true;
      try {
        const response = await fetchMessageHistory(this.nextHistoryUrl);

        if (response && Array.isArray(response.results)) {
          // Backend zwraca [msg10, msg9, msg8]. My chcemy mieć w tablicy [..., msg8, msg9, msg10].
          // Dlatego odwracamy kolejność pobranego fragmentu i dodajemy go na początek (`unshift`).
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
    // --- KONIEC ZMIAN w fetchHistory ---

    connect() {
      if (this.socket && this.status === 'open') return;

      // Resetujemy stan czatu przy każdym nowym połączeniu
      this.clearChatState();

      const authStore = useAuthStore();
      const token = authStore.accessToken;

      if (!token) {
        console.error("Cannot connect WS: no token");
        return;
      }

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const url = `${protocol}//localhost:8000/ws/chat/?token=${token}`;

      this.socket = new WebSocket(url);
      this.status = "connecting";

      this.socket.onopen = () => {
        this.status = "open";
        console.log("WebSocket connected");
      };

      // --- POCZĄTEK ZMIAN w handlerach ---
      // Usunąłem zduplikowane handlery. Zostawiamy tylko te bardziej rozbudowane.
      this.socket.onmessage = (event) => {
        try {
          const newMessage: Message = JSON.parse(event.data);
          // Nowa wiadomość ZAWSZE jest najnowsza, więc dodajemy ją na koniec.
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
        console.log('WebSocket connection closed.');
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.status = 'closed';
        this.socket = null; // Ważne, żeby też tutaj wyzerować socket
      };
      // --- KONIEC ZMIAN w handlerach ---
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

    // --- NOWA AKCJA ---
    // Akcja do czyszczenia stanu - przydatna przy wylogowaniu lub ponownym połączeniu
    clearChatState() {
      this.messages = [];
      this.nextHistoryUrl = INITIAL_HISTORY_URL;
      this.isLoadingHistory = false;
    }
  },
});
