type TranslationFunction = (key: string) => string;

type DataTableHeader = {
  title: string;
  key: string;
  sortable?: boolean;
  align?: 'start' | 'center' | 'end';
};

export const getManufacturerHeaders = (t: TranslationFunction): DataTableHeader[] => [
  { title: t('manufacturers.headers.name'), key: 'name', sortable: true },
];
