export interface Client {
  id: number;
  name: string;
  address: string;
  nip: string;
  phone_number: string;
  email: string;
  regon: string;
  created_at: string; // ISO datetime (np. "2025-10-27T10:15:00Z")
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
  user: User | null; // Ważne: user może być null
  first_name: string;
  last_name: string;
  email: string;
  phone_number: string;
  is_active: boolean;
  role: 'admin' | 'technician';
  role_display: string;
  full_name: string; // To jest @property, zawsze będzie stringiem
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

export interface ServiceTicket {
  id: number;
  ticket_number: string;
  title: string;
  description: string;
  ticket_type: string;
  status: string;
  resolution_notes: string;
  created_at: string;
  scheduled_for: string | null;
  completed_at: string | null;
  client: { id: number; name: string; nip: string };
  device_info: string;
  device: number;
  assigned_technician: { id: number; full_name: string } | null;
}

export type ClientPayload = Omit<Client, 'id' | 'created_at'> & {
  regon?: string;
  phone_number?: string;
  email?: string;
};

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
}

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  technician_profile: NestedTechnicianProfile | null
}
