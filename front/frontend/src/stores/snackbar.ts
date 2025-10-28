import { defineStore } from 'pinia';

interface SnackbarState {
  text: string;
  color: 'success' | 'info' | 'warning' | 'error';
  show: boolean;
}

export const useSnackbarStore = defineStore('snackbar', {
  state: (): SnackbarState => ({
    text: '',
    color: 'success',
    show: false,
  }),
  actions: {
    showSnackbar(text: string, color: SnackbarState['color'] = 'success') {
      this.text = text;
      this.color = color;
      this.show = true;
    },
    showSuccess(text: string) {
      this.showSnackbar(text, 'success');
    },
    showInfo(text: string) {
      this.showSnackbar(text, 'info');
    },
    showError(text: string) {
      this.showSnackbar(text, 'error');
    },
  },
});
