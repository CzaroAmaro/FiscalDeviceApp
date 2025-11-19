import type { ChartDataResponse } from '@/types'; // Za chwilę dodamy ten typ

import api from './index';

export const getChartData = async (): Promise<ChartDataResponse> => {
  // Poprawne wywołanie, bez /api/ na początku
  const response = await api.get<ChartDataResponse>('/charts/');
  return response.data;
};
