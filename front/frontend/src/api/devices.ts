import download from 'downloadjs';

import type { DevicePayload, FiscalDevice, PaginatedResponse,TechnicianSummary } from '@/types';

import apiClient from './index';
import api from './index';

export const sendInspectionReminders = async (deviceIds: number[]): Promise<any> => {
  const response = await api.post('/devices/send-reminders/', {
    device_ids: deviceIds,
  });
  return response.data;
};

export const getDevicesForSelect = async (filters: { clients?: number[], brands?: number[] } = {}): Promise<FiscalDevice[]> => {
  const params = new URLSearchParams();
  if (filters.clients && filters.clients.length > 0) {
    params.append('owner__id__in', filters.clients.join(','));
  }
  if (filters.brands && filters.brands.length > 0) {
    params.append('brand__id__in', filters.brands.join(','));
  }
  params.append('limit', '1000');

  try {
    const res = await api.get('/devices/', { params });

    const data = res.data;
    if (Array.isArray(data)) {
      return data as FiscalDevice[];
    }
    if (data && Array.isArray((data as any).results)) {
      return (data as any).results as FiscalDevice[];
    }

    console.warn('[getDevicesForSelect] Unexpected response shape for /devices/:', data);
    return [];
  } catch (error) {
    console.error('[getDevicesForSelect] Błąd pobierania /devices/:', error);
    return [];
  }
};

export const downloadDeviceReport = async (deviceId: number): Promise<void> => {
  try {
    const response = await api.get(`/devices/${deviceId}/export-pdf/`, {
      responseType: 'blob',
    });

    const contentDisposition = response.headers['content-disposition'];
    let filename = `raport_urzadzenia_${deviceId}.pdf`;
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/);
      if (filenameMatch?.[1]) {
        filename = filenameMatch[1];
      }
    }
    download(response.data, filename, 'application/pdf');
  } catch (error) {
    console.error('Błąd podczas pobierania raportu PDF:', error);
    throw new Error('Nie udało się pobrać raportu.');
  }
};

export const getEligibleTechnicians = (deviceId: number): Promise<TechnicianSummary[]> => {
  return apiClient.get(`/devices/${deviceId}/eligible-technicians/`).then(res => res.data);
};

export const performDeviceService = (deviceId: number, technicianId: number): Promise<FiscalDevice> => {
  return apiClient.post(`/devices/${deviceId}/perform-service/`, { technician_id: technicianId }).then(res => res.data);
};
