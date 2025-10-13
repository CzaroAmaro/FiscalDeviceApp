import type { Composer } from 'vue-i18n';

export const deviceHeaders = (t: Composer['t']) => [
  { title: t('devices.headers.model'), key: 'model_name', sortable: true },
  { title: t('devices.headers.serialNumber'), key: 'serial_number', sortable: true },
  { title: t('devices.headers.owner'), key: 'owner_name', sortable: true },
  { title: t('devices.headers.status'), key: 'status', sortable: true },
  { title: t('devices.headers.prodDate'), key: 'production_date', sortable: false },
  { title: t('devices.headers.lastService'), key: 'last_service_date', sortable: true }
];
