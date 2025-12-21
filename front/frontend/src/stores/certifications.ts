import { defineStore } from 'pinia';

import * as api from '@/api/certifications';
import type { Certification, CertificationPayload } from '@/types';

export class ApiValidationError extends Error {
  fieldErrors: Record<string, string[]>;

  constructor(errors: Record<string, string[]>) {
    const messages = Object.values(errors).flat().join(', ');
    super(messages);
    this.name = 'ApiValidationError';
    this.fieldErrors = errors;
  }
}

interface CertificationsState {
  certifications: Certification[];
  isLoading: boolean;
  error: string | null;
}

export const useCertificationsStore = defineStore('certifications', {
  state: (): CertificationsState => ({
    certifications: [],
    isLoading: false,
    error: null,
  }),

  actions: {
    async fetchCertifications(force = false) {
      if (this.certifications.length > 0 && !force) return;

      this.isLoading = true;
      this.error = null;
      try {
        this.certifications = await api.getCertifications();
      } catch (err) {
        this.error = 'Nie udało się załadować certyfikatów.';
        console.error(err);
      } finally {
        this.isLoading = false;
      }
    },

    async addCertification(payload: CertificationPayload) {
      try {
        const newCertification = await api.addCertification(payload);
        this.certifications.unshift(newCertification);
        return newCertification;
      } catch (error: any) {
        if (error.response?.status === 400 && error.response?.data) {
          throw new ApiValidationError(error.response.data);
        }
        throw error;
      }
    },

    async updateCertification(id: number, payload: CertificationPayload) {
      try {
        const updatedCertification = await api.updateCertification(id, payload);
        const index = this.certifications.findIndex(c => c.id === id);
        if (index !== -1) {
          this.certifications[index] = updatedCertification;
        }
        return updatedCertification;
      } catch (error: any) {
        if (error.response?.status === 400 && error.response?.data) {
          throw new ApiValidationError(error.response.data);
        }
        throw error;
      }
    },

    async deleteCertification(id: number) {
      await api.deleteCertification(id);
      this.certifications = this.certifications.filter(c => c.id !== id);
    },
  },
});
