import {
  keepPreviousData,
  QueryFunctionContext,
  useQuery,
} from "@tanstack/react-query";
import axios from "axios";
import { useState } from "react";
import fallbackCsvRaw from "../../data/vm_pricing.csv?raw";

import {
  FilterSection,
  FilterState,
} from "@/components/VMFinder/FilterSection";
import { Header } from "@/components/VMFinder/Header";
import { ResultsTable } from "@/components/VMFinder/ResultsTable";
import { FilterOptions, VMInstance } from "@/types";

const API_URL = import.meta.env.VITE_API_BASE_URL;
const ITEMS_PER_PAGE = 25;
const REQUEST_TIMEOUT_MS = 6000;
const HETZNER_BARE_METAL_PROVIDER = "Hetzner Bare Metal";
let forceFallbackMode = false;

const apiClient = axios.create({
  timeout: REQUEST_TIMEOUT_MS,
});

interface InstancesResponse {
  total: number;
  instances: VMInstance[];
}

const parseCsvLine = (line: string): string[] => {
  const result: string[] = [];
  let current = "";
  let inQuotes = false;

  for (let i = 0; i < line.length; i += 1) {
    const char = line[i];

    if (char === '"') {
      if (inQuotes && line[i + 1] === '"') {
        current += '"';
        i += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }

    if (char === "," && !inQuotes) {
      result.push(current);
      current = "";
      continue;
    }

    current += char;
  }

  result.push(current);
  return result;
};

const toNumberOrNull = (value: string | undefined): number | null => {
  if (!value) return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
};

const fallbackInstances: VMInstance[] = fallbackCsvRaw
  .split(/\r?\n/)
  .slice(1)
  .filter((line) => line.trim().length > 0)
  .map((line, index) => {
    const row = parseCsvLine(line);

    return {
      id: index + 1,
      instance_name: row[0] ?? "",
      provider: row[1] ?? "",
      region: row[2] ?? "",
      vcpus: toNumberOrNull(row[3]),
      memory_gb: toNumberOrNull(row[4]),
      storage_gb: toNumberOrNull(row[5]),
      storage_type: row[6] || null,
      hourly_cost: toNumberOrNull(row[7]),
      monthly_cost: toNumberOrNull(row[8]),
      spot_price: toNumberOrNull(row[9]),
      currency: row[10] ?? "USD",
      instance_family: row[11] || null,
      network_performance: row[12] || null,
      last_updated: row[13] ?? new Date().toISOString(),
    };
  });

const fallbackFilterOptions: FilterOptions = {
  providers: Array.from(
    new Set(fallbackInstances.map((item) => item.provider)),
  ).sort(),
  regions: Array.from(
    new Set(fallbackInstances.map((item) => item.region)),
  ).sort(),
  instance_families: Array.from(
    new Set(
      fallbackInstances
        .map((item) => item.instance_family)
        .filter((value): value is string => Boolean(value)),
    ),
  ).sort(),
  storage_types: Array.from(
    new Set(
      fallbackInstances
        .map((item) => item.storage_type)
        .filter((value): value is string => Boolean(value)),
    ),
  ).sort(),
};

const fetchFilterOptions = async (): Promise<FilterOptions> => {
  if (!API_URL || forceFallbackMode) {
    return fallbackFilterOptions;
  }

  try {
    const { data } = await apiClient.get(`${API_URL}/filters/options`);
    return data;
  } catch {
    forceFallbackMode = true;
    return fallbackFilterOptions;
  }
};

const fetchRegionsByProvider = async (provider: string): Promise<string[]> => {
  if (!API_URL) {
    return [];
  }

  try {
    const params = new URLSearchParams();
    params.append("provider", provider);
    const { data } = await apiClient.get(`${API_URL}/regions`, { params });
    return (Array.isArray(data) ? data : []).filter(Boolean).sort();
  } catch {
    return [];
  }
};

type InstancesQueryKey = [string, FilterState, number];

const buildFallbackInstancesResponse = (
  filters: FilterState,
  page: number,
): InstancesResponse => {
  const filtered = fallbackInstances
    .filter((item) => {
      if (
        filters.instanceName &&
        !item.instance_name
          .toLowerCase()
          .includes(filters.instanceName.toLowerCase())
      ) {
        return false;
      }

      if (filters.minVCPUs && (item.vcpus ?? 0) < Number(filters.minVCPUs)) {
        return false;
      }

      if (
        filters.minMemory &&
        (item.memory_gb ?? 0) < Number(filters.minMemory)
      ) {
        return false;
      }

      if (
        filters.providers.length > 0 &&
        !filters.providers.includes(item.provider)
      ) {
        return false;
      }

      if (
        filters.regions.length > 0 &&
        !filters.regions.includes(item.region)
      ) {
        return false;
      }

      return true;
    })
    .sort((a, b) => {
      const aHourly = a.hourly_cost ?? Number.POSITIVE_INFINITY;
      const bHourly = b.hourly_cost ?? Number.POSITIVE_INFINITY;

      if (aHourly !== bHourly) {
        return aHourly - bHourly;
      }

      return a.instance_name.localeCompare(b.instance_name);
    });

  const start = (page - 1) * ITEMS_PER_PAGE;
  const end = start + ITEMS_PER_PAGE;

  return {
    total: filtered.length,
    instances: filtered.slice(start, end),
  };
};

const fetchInstances = async ({
  queryKey,
}: QueryFunctionContext<InstancesQueryKey>): Promise<InstancesResponse> => {
  const [_key, filters, page] = queryKey;

  const params = new URLSearchParams();
  params.append("offset", ((page - 1) * ITEMS_PER_PAGE).toString());
  params.append("limit", ITEMS_PER_PAGE.toString());

  if (filters.instanceName)
    params.append("instance_name", filters.instanceName);
  if (filters.minVCPUs) params.append("min_vcpus", filters.minVCPUs);
  if (filters.minMemory) params.append("min_memory", filters.minMemory);
  filters.providers.forEach((p) => params.append("providers", p));
  filters.regions.forEach((r) => params.append("regions", r));

  if (!API_URL || forceFallbackMode) {
    return buildFallbackInstancesResponse(filters, page);
  }

  try {
    const { data } = await apiClient.get(`${API_URL}/instances`, { params });
    return data;
  } catch {
    forceFallbackMode = true;
    return buildFallbackInstancesResponse(filters, page);
  }
};

const Index = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [activeFilters, setActiveFilters] = useState<FilterState>({
    instanceName: "",
    minVCPUs: "",
    minMemory: "",
    regions: [],
    providers: [],
  });

  const { data: filterOptionsData, isLoading: isLoadingFilters } =
    useQuery<FilterOptions>({
      queryKey: ["filterOptions"],
      queryFn: fetchFilterOptions,
    });

  const {
    data: instancesData,
    isLoading: isLoadingInstances,
    isError,
  } = useQuery<InstancesResponse, Error, InstancesResponse, InstancesQueryKey>({
    queryKey: ["instances", activeFilters, currentPage],
    queryFn: fetchInstances,
    placeholderData: keepPreviousData,
  });

  const handleSearch = (newFilters: FilterState) => {
    setActiveFilters(newFilters);
    setCurrentPage(1);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const cloudProviders = (filterOptionsData?.providers || []).filter(
    (provider) => provider !== HETZNER_BARE_METAL_PROVIDER,
  );
  if (!cloudProviders.includes("Hetzner Cloud")) {
    cloudProviders.push("Hetzner Cloud");
    cloudProviders.sort();
  }
  const instances = instancesData?.instances || [];
  const totalResults = instancesData?.total || 0;
  const totalPages = Math.ceil(totalResults / ITEMS_PER_PAGE);

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container mx-auto max-w-content px-6 py-8 space-y-8">
        <FilterSection
          onSearch={handleSearch}
          providers={cloudProviders}
          regions={filterOptionsData?.regions || []}
          isLoading={isLoadingFilters}
        />

        <ResultsTable
          instances={instances}
          isLoading={isLoadingInstances}
          isError={isError}
          currentPage={currentPage}
          totalPages={totalPages}
          totalResults={totalResults}
          onPageChange={handlePageChange}
        />
      </main>
    </div>
  );
};

export default Index;
