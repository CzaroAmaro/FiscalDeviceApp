import type { RouteLocationRaw } from 'vue-router'

export interface MenuItem {
  title?: string;
  value?: string;
  icon?: string;
  to?: RouteLocationRaw;
  divider?: boolean;
  children?: MenuItem[];
}

/**
 * Zwraca przetłumaczoną listę elementów menu nawigacyjnego.
 * @param t - Funkcja tłumacząca z useI18n.
 * @returns Tablica obiektów MenuItem.
 */
export const getMenuItems = (t: (key: string) => string): MenuItem[] => [
  {
    title: t('menu.dashboard'),
    value: 'home',
    icon: 'mdi-view-dashboard',
    to: { name: 'home' },
  },
  {
    title: t('menu.devices'),
    value: 'devices',
    icon: 'mdi-printer-pos',
    to: { name: 'device-list' },
  },
  {
    title: t('menu.clients'),
    value: 'clients',
    icon: 'mdi-account-group-outline',
    to: { name: 'client-list' },
  },
  {
    title: t('menu.manufacturers'),
    value: 'manufacturers',
    icon: 'mdi-factory',
    to: { name: 'manufacturer-list' },
  },
  {
    title: t('Pracownicy'),
    icon: 'mdi-briefcase-account',
    children: [
      {
        title: t('menu.technicians'),
        value: 'technicians',
        icon: 'mdi-account-hard-hat',
        to: { name: 'technician-list' },
      },
      {
        title: t('Certyfikaty'),
        value: 'certifications',
        icon: 'mdi-lock-check-outline',
        to: { name: 'certification-list' },
      },
    ],
  },
  {
    title: t('menu.tickets'),
    value: 'tickets',
    icon: 'mdi-ticket-confirmation-outline',
    to: { name: 'ticket-list' },
  },
];
