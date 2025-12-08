import type { ReportFilterOptions, ReportParameters, ReportResult } from '@/types'; // Musimy zdefiniować te typy

import api from './index';

/**
 * Pobiera opcje dostępne do filtrowania w generatorze raportów.
 */
export async function getReportFilterOptions(): Promise<ReportFilterOptions> {
  const response = await api.get<ReportFilterOptions>('/reports/filter-options/');
  return response.data;
}

/**
 * Generuje raport na podstawie podanych parametrów.
 * @param params - Obiekt z parametrami raportu.
 */
export async function generateReport(params: ReportParameters): Promise<ReportResult[]> {
  const response = await api.post<ReportResult[]>('/reports/generate/', params);
  return response.data;
}

/**
 * Generuje i pobiera raport w formacie pliku (PDF lub CSV).
 * @param params - Obiekt z parametrami raportu.
 * @param format - 'pdf' lub 'csv'
 */
export async function downloadReport(params: ReportParameters, format: 'pdf' | 'csv'): Promise<void> {
  const finalParams: ReportParameters = {
    ...params,
    output_format: format
  };

  const response = await api.post('/reports/generate/', finalParams, {
    responseType: 'blob'
  });

  const blob = new Blob([response.data], { type: response.headers['content-type'] });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;

  const contentDisposition = response.headers['content-disposition'];
  let fileName = format === 'pdf' ? 'raport.pdf' : 'raport.csv';
  if (contentDisposition) {
    const fileNameMatch = contentDisposition.match(/filename="(.+)"/);
    if (fileNameMatch && fileNameMatch.length > 1) {
      fileName = fileNameMatch[1];
    }
  }

  link.setAttribute('download', fileName);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}
