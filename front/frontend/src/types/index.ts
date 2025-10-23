import type { RouteLocationRaw } from "vue-router";

export interface FiscalDevice {
  id: number;
  brand: number;
  brand_name: string;
  model_name: string;
  unique_number: string;
  serial_number: string;
  sale_date: string;
  last_service_date: string | null;
  status: string;
  operating_instructions: string;
  remarks: string;
  owner: number;
  owner_name: string;
  tickets: ServiceTicket[];
}

export interface MenuItem {
    title: string;
    value: string;
    icon: string;
    to: RouteLocationRaw;
    divider?: boolean;
}

export interface Client {
  id: number;
  name: string;
  address: string;
  nip: string;
  phone_number: string;
  email: string;
  regon: string;
  created_at: string;
}
export interface Manufacturer {
  id: number;
  name: string;
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
  user: User; // Zagnieżdżone dane użytkownika
  phone_number: string;
  is_active: boolean;
}

export interface Certification {
  id: number;
  technician: number; // ID serwisanta
  manufacturer: number; // ID producenta
  certificate_number: string;
  issue_date: string;
  expiry_date: string;
}

export interface ServiceTicket {
  id: number;
  ticket_number: string;
  title: string;
  description: string;
  ticket_type: string;
  status: string;
  client: number; // ID klienta
  client_name: string;
  device: number; // ID urządzenia
  device_info: string;
  assigned_technician: number | null; // ID serwisanta
  technician_name: string | null;
  created_at: string;
  resolution_notes: string;
  scheduled_for: string | null;
  completed_at: string | null;
}

export interface MenuItem {
  title: string;
  value: string;
  icon: string;
  to: RouteLocationRaw;
  divider?: boolean;
}
