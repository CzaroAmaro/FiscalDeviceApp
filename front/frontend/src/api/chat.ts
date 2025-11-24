import type { Message, PaginatedResponse } from '@/types';

import api from './index';

/**
 * Pobiera historię wiadomości z paginacją.
 * @param url - Pełny URL do strony z wiadomościami (np. /api/messages/?limit=50&offset=50)
 */
export const fetchMessageHistory = async (url: string): Promise<PaginatedResponse<Message>> => {
  // Używamy 'await' i zwracamy bezpośrednio 'data' z odpowiedzi
  const response = await api.get<PaginatedResponse<Message>>(url);
  return response.data;
};
