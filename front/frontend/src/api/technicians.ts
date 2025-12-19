import api from '@/api';
import type { TechnicianStats } from '@/types';

export async function fetchTechnicianStats(technicianId: number): Promise<TechnicianStats> {
  const response = await api.get<TechnicianStats>(`/technicians/${technicianId}/stats/`);
  return response.data;
}
