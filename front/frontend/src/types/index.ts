import type { RouteLocationRaw } from 'vue-router'

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
  name:string;
}

export interface FiscalDevice {
  id: number;
  model_name: string;
  unique_number: string;
  serial_number: string;
  sale_date: string;
  last_service_date: string | null;
  status: string; // Np. "Aktywna", "W serwisie" - czytelna nazwa z backendu
  operating_instructions: string;
  remarks: string;
  // Zagnieżdżone obiekty dla łatwego wyświetlania
  owner: { id: number; name: string; nip: string }; // Używamy ClientSummarySerializer
  brand: { id: number; name: string };             // Używamy ManufacturerSerializer
  tickets_count: number; // Zastąpiliśmy pełną listę zgłoszeń licznikiem
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
  user: User;
  phone_number: string;
  is_active: boolean;
  // DOBRA PRAKTYKA: Dodajmy pole, które backend może łatwo dostarczyć
  full_name: string; // np. "Jan Kowalski" z `technician.__str__()`
}

export interface Certification {
  id: number;
  certificate_number: string;
  issue_date: string;
  expiry_date: string;
  // Zagnieżdżone obiekty dla czytelności
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
  // Zagnieżdżone obiekty dla czytelności
  client: { id: number; name: string; nip: string };
  device_info: string;
  device: number; // ID urządzenia nadal jest przydatne
  assigned_technician: { id: number; full_name: string } | null;
}

// Interfejs pomocniczy dla menu
export interface MenuItem {
  title: string;
  value: string;
  icon: string;
  to: RouteLocationRaw;
  divider?: boolean;
}

// =================================================================
// TYPY DO ZAPISU (Write Models / Payloads) - Używane w żądaniach POST/PUT
// =================================================================

// Pola wymagane do utworzenia/edycji klienta
export type ClientPayload = Omit<Client, 'id' | 'created_at'>;

// Pola wymagane do utworzenia/edycji urządzenia (tylko ID dla relacji)
export type DevicePayload = Pick<
  FiscalDevice,
  'model_name' | 'unique_number' | 'serial_number' | 'sale_date' | 'last_service_date' | 'status' | 'operating_instructions' | 'remarks'
> & {
  owner: number; // Oczekujemy ID
  brand: number; // Oczekujemy ID
};

// Pola wymagane do utworzenia/edycji zgłoszenia (tylko ID dla relacji)
export type ServiceTicketPayload = Pick<
  ServiceTicket,
  'title' | 'description' | 'ticket_type' | 'status' | 'scheduled_for' | 'resolution_notes'
> & {
  client: number;
  device: number;
  assigned_technician: number | null;
};

// Pola do rejestracji
export interface RegisterCredentials {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}
