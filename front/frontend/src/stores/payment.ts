import { defineStore } from 'pinia';

import { createCheckoutSession } from '@/api/payments';

interface PaymentState {
  isPurchasing: boolean;
  error: string | null;
}

export const usePaymentStore = defineStore('payment', {
  state: (): PaymentState => ({
    isPurchasing: false,
    error: null,
  }),

  actions: {
    async startPurchase() {
      this.isPurchasing = true;
      this.error = null;
      try {
        const response = await createCheckoutSession();
        if (response.url) {
          window.location.href = response.url;
        } else {
          const errorMessage = "Błąd: Nie otrzymano adresu URL do płatności.";
          this.error = errorMessage;
          console.error(errorMessage, response.error);
        }
      } catch (error) {
        const errorMessage = "Nie udało się zainicjować płatności.";
        this.error = errorMessage;
        console.error(errorMessage, error);
        this.isPurchasing = false;
      }
    },
  },
});
