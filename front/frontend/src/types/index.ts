export interface FiscalDevice {
    id: number;
    model_name: string;
    serial_number: string;
    production_date: string;
    last_service_date: string | null;
    status: string;
    owner_name: string;
}

