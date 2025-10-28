type TranslationFunction = (key: string) => string;

type DataTableHeader = {
  title: string;
  key: string;
  sortable?: boolean;
  align?: 'start' | 'center' | 'end';
};

// Eksportujemy FUNKCJĘ, która przyjmuje `t` jako argument
export const getDeviceHeaders = (t: TranslationFunction): DataTableHeader[] => [
  // Używamy kluczy z plików .json
  { title: t('devices.headers.brand'), key: 'brand_name' },
  { title: t('devices.headers.model'), key: 'model_name' },
  { title: t('devices.headers.uniqueNumber'), key: 'unique_number' },
  { title: t('devices.headers.owner'), key: 'owner_name' },
  { title: t('devices.headers.status'), key: 'status' },
  { title: t('devices.headers.saleDate'), key: 'sale_date' },
];
