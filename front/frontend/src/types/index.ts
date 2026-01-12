export interface Client {
  id: number;
  name: string;
  address: string;
  nip: string;
  phone_number: string;
  email: string;
  regon: string;
  created_at: string;
  latitude: number | null;
  longitude: number | null;
}

export interface ClientLocation {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  has_open_tickets: boolean;
}

export interface Manufacturer {
  id: number;
  name: string;
}

export interface FiscalDevice {
  id: number;
  model_name: string;
  unique_number: string;
  serial_number: string;
  sale_date: string;
  last_service_date: string | null;
  status: string;
  operating_instructions: string;
  remarks: string;

  owner: {
    id: number;
    name: string;
    nip: string;
  };

  brand: {
    id: number;
    name: string;
  };

  tickets_count: number;
}

export interface User {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
}

export interface Technician {
  id: number;
  user: User | null;
  first_name: string;
  last_name: string;
  email: string;
  phone_number: string;
  is_active: boolean;
  role: 'admin' | 'technician';
  role_display: string;
  full_name: string;
}

export interface TechnicianPayload {
  first_name: string;
  last_name: string;
  email: string;
  phone_number: string;
  role: 'admin' | 'technician';
  is_active: boolean;
  create_user_account?: boolean;
  username?: string;
  password?: string;
}

export interface Certification {
  id: number;
  certificate_number: string;
  issue_date: string;
  expiry_date: string;
  technician: number;
  technician_name: string;
  manufacturer: number;
  manufacturer_name: string;
}

export type CertificationPayload = Pick<
  Certification,
  'certificate_number' | 'issue_date' | 'expiry_date'
> & {
  technician: number;
  manufacturer: number;
};

export interface ServiceTicket {
  id: number;
  ticket_number: string;
  title: string;
  description: string;
  ticket_type: string;
  ticket_type_display: string;
  status: string;
  status_display: string;
  resolution_notes: string;
  created_at: string;
  scheduled_for: string | null;
  completed_at: string | null;
  client: { id: number; name: string; nip: string };
  device_info: string;
  device: number;
  assigned_technician: { id: number; full_name: string } | null;
  resolution: string;
  resolution_display: string;
}

export interface ClientPayload {
  name: string;
  address: string;
  nip: string;
  phone_number?: string;
  email?: string;
  regon?: string;
  latitude?: number | null;
  longitude?: number | null;
}

export type DevicePayload = Pick<
  FiscalDevice,
  | 'model_name'
  | 'unique_number'
  | 'serial_number'
  | 'sale_date'
  | 'last_service_date'
  | 'status'
  | 'operating_instructions'
  | 'remarks'
> & {
  owner: number;
  brand: number;
};

export type ServiceTicketPayload = Pick<
  ServiceTicket,
  | 'title'
  | 'description'
  | 'ticket_type'
  | 'status'
  | 'scheduled_for'
  | 'resolution_notes'
> & {
  client: number;
  device: number;
  assigned_technician: number | null;
};

export interface RegisterCredentials {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}
export interface NestedTechnicianProfile {
  id: number;
  company: number;
  is_admin: boolean
}

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  technician_profile: NestedTechnicianProfile | null
}

export interface ChartDataResponse {
  tickets_by_status: {
    labels: string[];
    data: number[];
  };
  workload_over_time: {
    labels: string[];
    datasets: {
      label: string;
      data: number[];
      backgroundColor: string;
      borderColor: string;
    }[];
  };
  devices_by_status: {
    labels: string[];
    data: number[];
  };
  expiring_certifications: {
    technician: string;
    manufacturer: string;
    certificate_number: string;
    expiry_date: string;
  }[];
}
export interface TicketResolutionPayload {
  resolution: string;
  resolution_notes?: string;
}

export interface Message {
  id: number;
  sender_id: number;
  sender_name: string;
  content: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ReportParameters {
  date_from?: string;
  date_to?: string;
  clients?: number[];
  devices?: number[];
  device_brands?: number[];
  include_service_history?: boolean;
  history_date_from?: string;
  history_date_to?: string;
  include_event_log?: boolean;
  output_format?: 'json' | 'csv' | 'pdf';
}

export interface ReportFilterOptions {
  clients: { id: number; name: string }[];
  technicians: { id: number; name: string }[];
  brands: { id: number; name: string }[];
  ticket_statuses: { value: string; text: string }[];
  ticket_types: { value: string; text: string }[];
  ticket_resolutions: { value: string; text: string }[];
}

export interface ReportResult {
  ticket_number: string;
  title: string;
  created_at: string;
  scheduled_for: string | null;
  completed_at: string | null;
  client_name: string;
  client_nip: string;
  device_model: string;
  device_unique_number: string;
  assigned_technician_name: string | null;
  status_display: string;
  ticket_type_display: string;
  resolution_display: string;
}

export interface TechnicianSummary {
  id: number;
  full_name: string;
}

export interface ClientStats {
  devices_count: number;
  tickets_count: number;
  open_tickets_count: number;
}

export interface TechnicianStats {
  assigned_tickets_count: number;
  open_tickets_count: number;
  in_progress_tickets_count: number;
  closed_tickets_count: number;
  valid_certifications_count: number;
  expiring_soon_count: number;
  expired_certifications_count: number;
}
