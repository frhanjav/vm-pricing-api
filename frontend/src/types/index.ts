export interface VMInstance {
  id: number;
  instance_name: string;
  provider: string;
  region: string;
  vcpus: number | null;
  memory_gb: number | null;
  storage_gb: number | null;
  storage_type: string | null;
  hourly_cost: number | null;
  monthly_cost: number | null;
  spot_price: number | null;
  currency: string;
  instance_family: string | null;
  network_performance: string | null;
  last_updated: string;
}

export interface FilterOptions {
  providers: string[];
  regions: string[];
  instance_families: string[];
  storage_types: string[];
}