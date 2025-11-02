type TranslationFunction = (key: string) => string;

type DataTableHeader = {
  title: string;
  key: string;
  sortable?: boolean;
  align?: 'start' | 'center' | 'end';
};

export const getClientHeaders = (t: TranslationFunction): DataTableHeader[] => [
  { title: t('clients.headers.id'), key: 'id', sortable: true },
  { title: t('clients.headers.name'), key: 'name', sortable: true },
  { title: t('clients.headers.nip'), key: 'nip', sortable: true },
  { title: t('clients.headers.phone'), key: 'phone_number', sortable: false },
  { title: t('clients.headers.email'), key: 'email', sortable: true },
];
