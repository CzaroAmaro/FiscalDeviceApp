type TranslationFunction = (key: string) => string;

type DataTableHeader = {
  title: string;
  key: string;
  sortable?: boolean;
  align?: 'start' | 'center' | 'end';
};

export const getCertificationHeaders = (t: TranslationFunction): DataTableHeader[] => [
  {  title: t('certifications.headers.id'),  key: 'id', sortable: true },
  { title: t('certifications.headers.certificateNumber'),  key: 'certificate_number' },
  { title: t('certifications.headers.technician'), key: 'technician_name' },
  { title: t('certifications.headers.manufacturer'),  key: 'manufacturer_name' },
  { title: t('certifications.headers.issueDate'),  key: 'issue_date' },
  { title: t('certifications.headers.expiryDate'), key: 'expiry_date' },
];
