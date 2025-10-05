import type {RouteLocationRaw} from "vue-router";

export interface FiscalDevice {
    id: number;
    model_name: string;
    serial_number: string;
    production_date: string;
    last_service_date: string | null;
    status: string;
    owner_name: string;
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
