type TranslationFunction = (key: string) => string;

type DataTableHeader = {
  title: string;
  key: string;
  sortable?: boolean;
  align?: 'start' | 'center' | 'end';
  width?: string | number;
};

export const getTechnicianHeaders = (t: TranslationFunction): DataTableHeader[] => [
  { title: ('ID'), key: 'id', sortable: true },
  { title: t('technicians.headers.fullName'), key: 'full_name', sortable: true },
  { title: t('technicians.headers.phone'), key: 'phone_number', sortable: false },
  { title: t('technicians.headers.email'), key: 'user.email', sortable: true }, // Dostęp do zagnieżdżonego pola
  { title: t('technicians.headers.status'), key: 'is_active', sortable: true },
];
