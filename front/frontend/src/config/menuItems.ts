import type { Composer } from 'vue-i18n';
import type { MenuItem } from '@/types';

/**
 * Zwraca przetłumaczoną listę elementów menu nawigacyjnego.
 * @param t - Funkcja tłumacząca z useI18n.
 * @returns Tablica obiektów MenuItem.
 */
export const getMenuItems = (t: Composer['t']): MenuItem[] => [
  {
    title: t('menu.dashboard'),
    value: 'dashboard',
    icon: 'mdi-view-dashboard',
    to: { name: 'home' },
  },
  {
    title: t('menu.devices'),
    value: 'devices',
    icon: 'mdi-printer-pos',
    to: { name: 'devices' },
  },
  {
    title: t('menu.clients'),
    value: 'clients',
    icon: 'mdi-account-group-outline',
    to: { name: 'clients' },
  },
  // { divider: true },
];
