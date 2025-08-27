import {
  keepPreviousData,
  QueryFunctionContext,
  useQuery,
} from "@tanstack/react-query";
import axios from "axios";
import { useState } from "react";

import {
  FilterSection,
  FilterState,
} from "@/components/VMFinder/FilterSection";
import { Header } from "@/components/VMFinder/Header";
import { ResultsTable } from "@/components/VMFinder/ResultsTable";
import { FilterOptions, VMInstance } from "@/types";

const API_URL = import.meta.env.VITE_API_BASE_URL;
const ITEMS_PER_PAGE = 25;

interface InstancesResponse {
  total: number;
  instances: VMInstance[];
}

const fetchFilterOptions = async (): Promise<FilterOptions> => {
  const { data } = await axios.get(`${API_URL}/filters/options`);
  return data;
};

type InstancesQueryKey = [string, FilterState, number];

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

  const { data } = await axios.get(`${API_URL}/instances`, { params });
  return data;
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

  const instances = instancesData?.instances || [];
  const totalResults = instancesData?.total || 0;
  const totalPages = Math.ceil(totalResults / ITEMS_PER_PAGE);

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container mx-auto max-w-content px-6 py-8 space-y-8">
        <FilterSection
          onSearch={handleSearch}
          providers={filterOptionsData?.providers || []}
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
