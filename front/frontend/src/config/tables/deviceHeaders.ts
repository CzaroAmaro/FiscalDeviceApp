import type { Composer } from 'vue-i18n';

export const deviceHeaders = [
  { title: 'Marka', key: 'brand_name', sortable: true },
  { title: 'Model', key: 'model_name', sortable: true },
  { title: 'Numer unikatowy', key: 'unique_number', sortable: true },
  { title: 'Numer seryjny', key: 'serial_number', sortable: true },
  { title: 'Właściciel', key: 'owner_name', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Data produkcji', key: 'production_date', sortable: false },
  { title: 'Ostatni serwis', key: 'last_service_date', sortable: true },
  { title: 'Data sprzedaży', key: 'sale_date', sortable: true },

];
