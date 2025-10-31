type TranslationFunction = (key: string) => string;

type DataTableHeader = {
  title: string;
  key: string;
  sortable?: boolean;
  align?: 'start' | 'center' | 'end';
  width?: string | number;
};

export const getTicketHeaders = (t: TranslationFunction): DataTableHeader[] => [
  { title: ('ID'), key: 'id', sortable: true },
  { title: t('tickets.headers.ticketNumber'), key: 'ticket_number', sortable: true },
  { title: t('tickets.headers.title'), key: 'title', sortable: true },
  { title: t('tickets.headers.client'), key: 'client.name', sortable: true },
  { title: t('tickets.headers.status'), key: 'status', sortable: true },
  { title: t('tickets.headers.technician'), key: 'assigned_technician.full_name', sortable: true },
  { title: t('tickets.headers.created'), key: 'created_at', sortable: true },
];
