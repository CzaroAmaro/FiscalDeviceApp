import type { ChartDataResponse } from '@/types';

import api from './index';

export const getChartData = async (): Promise<ChartDataResponse> => {
  const response = await api.get<ChartDataResponse>('/charts/');
  return response.data;
};
