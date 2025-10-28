import type { Composer } from 'vue-i18n';
import type { RouteLocationRaw } from 'vue-router'

export interface MenuItem {
  title?: string;
  value?: string;
  icon?: string;
  to?: RouteLocationRaw;
  divider?: boolean;
}
/**
 * Zwraca przetłumaczoną listę elementów menu nawigacyjnego.
 * @param t - Funkcja tłumacząca z useI18n.
 * @returns Tablica obiektów MenuItem.
 */
export const getMenuItems = (t: Composer['t']): MenuItem[] => [
  {
    title: t('menu.dashboard'),
    value: 'home',
    icon: 'mdi-view-dashboard',
    to: { name: 'home' }, // Pasuje do name: 'home' w routerze
  },
  {
    title: t('menu.devices'),
    value: 'devices',
    icon: 'mdi-printer-pos',
    to: { name: 'device-list' }, // Pasuje do name: 'device-list' w routerze
  },
  {
    title: t('menu.clients'),
    value: 'clients',
    icon: 'mdi-account-group-outline',
    to: { name: 'client-list' }, // Pasuje do name: 'client-list' w routerze
  },
  // { divider: true },
];
