import type { Certification, CertificationPayload } from '@/types';

import api from './index';

export const getCertifications = async (): Promise<Certification[]> => {
  const response = await api.get<Certification[]>('/certifications/');
  return response.data;
};

export const addCertification = async (payload: CertificationPayload): Promise<Certification> => {
  const response = await api.post<Certification>('/certifications/', payload);
  return response.data;
};

export const updateCertification = async (id: number, payload: CertificationPayload): Promise<Certification> => {
  const response = await api.put<Certification>(`/certifications/${id}/`, payload);
  return response.data;
};

export const deleteCertification = async (id: number): Promise<void> => {
  await api.delete(`/certifications/${id}/`);
};
