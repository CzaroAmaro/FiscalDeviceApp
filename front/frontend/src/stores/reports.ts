import { defineStore } from 'pinia';
import { ref } from 'vue';

import { downloadReport,generateReport, getReportFilterOptions } from '@/api/reports';
import type { ReportFilterOptions, ReportParameters, ReportResult } from '@/types';

const getDefaultParameters = (): ReportParameters => ({
  clients: [],
  device_brands: [],
  devices: [],
  include_service_history: false,
  history_date_from: undefined,
  history_date_to: undefined,
  include_event_log: false,
});

export const useReportsStore = defineStore('reports', () => {
  const parameters = ref<ReportParameters>(getDefaultParameters());
  const filterOptions = ref<ReportFilterOptions | null>(null);
  const results = ref<ReportResult[]>([]);
  const isLoading = ref(false);
  const isLoadingOptions = ref(false);
  const error = ref<string | null>(null);

  async function fetchFilterOptions() {
    isLoadingOptions.value = true;
    error.value = null;
    try {
      filterOptions.value = await getReportFilterOptions();
    } catch (e: any) {
      error.value = 'Nie udało się załadować opcji filtrowania. Spróbuj ponownie.';
    } finally {
      isLoadingOptions.value = false;
    }
  }

  async function runReport() {
    isLoading.value = true;
    error.value = null;
    results.value = [];
    try {
      results.value = await generateReport(parameters.value);
    } catch (e: any) {
      error.value = 'Wystąpił błąd podczas generowania raportu. Sprawdź parametry i spróbuj ponownie.';
    } finally {
      isLoading.value = false;
    }
  }

  async function exportReport(format: 'pdf' | 'csv') {
    isLoading.value = true;
    error.value = null;
    try {
      await downloadReport(parameters.value, format);
    } catch(e: any) {
      error.value = `Nie udało się wyeksportować raportu do ${format.toUpperCase()}.`;
    } finally {
      isLoading.value = false;
    }
  }

  function clearParameters() {
    parameters.value = getDefaultParameters();
  }


  return {
    parameters,
    filterOptions,
    isLoading,
    isLoadingOptions,
    error,
    fetchFilterOptions,
    exportReport,
    clearParameters,
  };
});
