import type {RouteLocationRaw} from "vue-router";

export interface FiscalDevice {
  id: number;
  model_name: string;
  serial_number: string;
  production_date: string;
  last_service_date: string | null;
  status: string;
  owner: number;
  owner_name: string;
  service_history: ServiceRecord[];
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
  created_at: string;
}

export interface ServiceRecord {
  id: number;
  description: string;
  service_date: string;
  technician_username: string;
}
