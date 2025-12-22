import type { Message, PaginatedResponse } from '@/types';

import api from './index';

export const fetchMessageHistory = async (url: string): Promise<PaginatedResponse<Message>> => {
  const response = await api.get<PaginatedResponse<Message>>(url);
  return response.data;
};
