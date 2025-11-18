import type { Certification, CertificationPayload } from '@/types';

import api from './index';

// Pobierz wszystkie certyfikaty
export const getCertifications = async (): Promise<Certification[]> => {
  const response = await api.get<Certification[]>('/certifications/');
  return response.data;
};

// Dodaj nowy certyfikat
export const addCertification = async (payload: CertificationPayload): Promise<Certification> => {
  const response = await api.post<Certification>('/certifications/', payload);
  return response.data;
};

// Zaktualizuj certyfikat
export const updateCertification = async (id: number, payload: CertificationPayload): Promise<Certification> => {
  const response = await api.put<Certification>(`/certifications/${id}/`, payload);
  return response.data;
};

// Usuń certyfikat
export const deleteCertification = async (id: number): Promise<void> => {
  await api.delete(`/certifications/${id}/`);
};
