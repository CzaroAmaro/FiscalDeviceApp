type TranslationFunction = (key: string) => string;

type DataTableHeader = {
  title: string;
  key: string;
  sortable?: boolean;
  align?: 'start' | 'center' | 'end';
};

export const getCertificationHeaders = (t: TranslationFunction): DataTableHeader[] => [
  { title: 'ID', key: 'id', sortable: true },
  { title: 'Numer certyfikatu', key: 'certificate_number' },
  { title: 'Serwisant', key: 'technician_name' },
  { title: 'Producent', key: 'manufacturer_name' },
  { title: 'Data wydania', key: 'issue_date' },
  { title: 'Data ważności', key: 'expiry_date' },
];
