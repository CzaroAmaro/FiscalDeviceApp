import download from 'downloadjs';

import api from './index'; // Twoja główna instancja Axios

/**
 * Pobiera raport PDF dla danego urządzenia i inicjuje pobieranie w przeglądarce.
 * @param deviceId ID urządzenia
 */
export const downloadDeviceReport = async (deviceId: number): Promise<void> => {
  try {
    const response = await api.get(`/devices/${deviceId}/export-pdf/`, {
      responseType: 'blob',
    });

    const contentDisposition = response.headers['content-disposition'];
    let filename = `raport_urzadzenia_${deviceId}.pdf`;
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/);
      if (filenameMatch && filenameMatch.length > 1) {
        filename = filenameMatch[1];
      }
    }

    download(response.data, filename, 'application/pdf');

  } catch (error) {
    console.error('Błąd podczas pobierania raportu PDF:', error);
    throw new Error('Nie udało się pobrać raportu.');
  }
};
