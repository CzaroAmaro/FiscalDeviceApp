import { defineStore } from 'pinia';
import { ref } from 'vue';

import { getChartData } from '@/api/charts';
import type { ChartDataResponse } from '@/types';

import { useSnackbarStore } from './snackbar';

export const useChartsStore = defineStore('charts', () => {
  const loading = ref<boolean>(false);
  const error = ref<string | null>(null);
  const data = ref<ChartDataResponse | null>(null);

  async function fetchChartData() {
    if (data.value) return;

    loading.value = true;
    error.value = null;
    const snackbarStore = useSnackbarStore();

    try {
      data.value = await getChartData();
    } catch (e: any) {
      error.value = 'Nie udało się załadować danych do wykresów.';
      snackbarStore.showSnackbar(error.value, 'error');
      console.error('Failed to fetch chart data:', e);
    } finally {
      loading.value = false;
    }
  }

  return {
    loading,
    error,
    data,
    fetchChartData
  };
});
