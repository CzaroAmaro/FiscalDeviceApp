import api from '@/api';
import type { ClientStats } from '@/types';

export async function fetchClientStats(clientId: number): Promise<ClientStats> {
  const response = await api.get<ClientStats>(`/clients/${clientId}/stats/`);
  return response.data;
}
