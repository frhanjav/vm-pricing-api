import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Search, Loader2 } from "lucide-react";

export interface FilterState {
  instanceName: string;
  minVCPUs: string;
  minMemory: string;
  regions: string[];
  providers: string[];
}

interface FilterSectionProps {
  onSearch: (filters: FilterState) => void;
  providers: string[];
  regions: string[];
  isLoading: boolean;
}

export const FilterSection: React.FC<FilterSectionProps> = ({
  onSearch,
  providers,
  regions,
  isLoading,
}) => {
  const [instanceName, setInstanceName] = useState("");
  const [minVCPUs, setMinVCPUs] = useState("");
  const [minMemory, setMinMemory] = useState("");
  const [selectedRegions, setSelectedRegions] = useState<string[]>([]);
  const [selectedProviders, setSelectedProviders] = useState<string[]>([]);

  const handleRegionToggle = (region: string) => {
    setSelectedRegions((prev) =>
      prev.includes(region)
        ? prev.filter((r) => r !== region)
        : [...prev, region],
    );
  };

  const handleProviderToggle = (provider: string) => {
    setSelectedProviders((prev) =>
      prev.includes(provider)
        ? prev.filter((p) => p !== provider)
        : [...prev, provider],
    );
  };

  const handleSearch = () => {
    onSearch({
      instanceName,
      minVCPUs,
      minMemory,
      regions: selectedRegions,
      providers: selectedProviders,
    });
  };

  const handleReset = () => {
    setInstanceName("");
    setMinVCPUs("");
    setMinMemory("");
    setSelectedRegions([]);
    setSelectedProviders([]);
    onSearch({
      instanceName: "",
      minVCPUs: "",
      minMemory: "",
      regions: [],
      providers: [],
    });
  };

  return (
    <Card className="shadow-card">
      <fieldset disabled={isLoading} className="group">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-foreground">
            <Search className="h-5 w-5 text-primary" />
            Search & Filter
            {isLoading && (
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6 group-disabled:opacity-50">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="instance-name">Instance Name</Label>
              <Input
                id="instance-name"
                placeholder="Search instances like t4g.nano..."
                value={instanceName}
                onChange={(e) => setInstanceName(e.target.value)}
                className="bg-background"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="min-vcpus">Min vCPUs</Label>
              <Input
                id="min-vcpus"
                type="number"
                placeholder="e.g., 2"
                value={minVCPUs}
                onChange={(e) => setMinVCPUs(e.target.value)}
                className="bg-background"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="min-memory">Min Memory (GB)</Label>
              <Input
                id="min-memory"
                type="number"
                placeholder="e.g., 4"
                value={minMemory}
                onChange={(e) => setMinMemory(e.target.value)}
                className="bg-background"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <Label className="text-sm font-medium">Regions</Label>
              <div className="max-h-32 overflow-y-auto bg-muted/30 rounded-lg p-3 space-y-2">
                {regions.map((region) => (
                  <div key={region} className="flex items-center space-x-2">
                    <Checkbox
                      id={`region-${region}`}
                      checked={selectedRegions.includes(region)}
                      onCheckedChange={() => handleRegionToggle(region)}
                    />
                    <Label
                      htmlFor={`region-${region}`}
                      className="text-sm cursor-pointer"
                    >
                      {region}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-3">
              <Label className="text-sm font-medium">Providers</Label>
              <div className="max-h-32 overflow-y-auto bg-muted/30 rounded-lg p-3 space-y-2">
                {providers.map((provider) => (
                  <div key={provider} className="flex items-center space-x-2">
                    <Checkbox
                      id={`provider-${provider}`}
                      checked={selectedProviders.includes(provider)}
                      onCheckedChange={() => handleProviderToggle(provider)}
                    />
                    <Label
                      htmlFor={`provider-${provider}`}
                      className="text-sm cursor-pointer"
                    >
                      {provider}
                    </Label>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <Button
              onClick={handleSearch}
              className="w-full md:w-auto bg-gradient-primary hover:shadow-hover transition-all duration-200"
            >
              <Search className="h-4 w-4 mr-2" />
              Search
            </Button>
            <Button
              variant="outline"
              onClick={handleReset}
              className="w-full md:w-auto"
            >
              Reset
            </Button>
          </div>
        </CardContent>
      </fieldset>
    </Card>
  );
};
