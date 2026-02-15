import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Search, Wrench, Loader2 } from "lucide-react";

export interface BareMetalFilterState {
  minCores: string;
  minMemory: string;
  minStorage: string;
  maxMonthlyCost: string;
  region: string;
}

interface BareMetalBuilderProps {
  onSearch: (filters: BareMetalFilterState) => void;
  regions: string[];
  isLoading: boolean;
}

export const BareMetalBuilder: React.FC<BareMetalBuilderProps> = ({
  onSearch,
  regions,
  isLoading,
}) => {
  const [minCores, setMinCores] = useState("");
  const [minMemory, setMinMemory] = useState("");
  const [minStorage, setMinStorage] = useState("");
  const [maxMonthlyCost, setMaxMonthlyCost] = useState("");
  const [region, setRegion] = useState("");

  const handleSearch = () => {
    onSearch({ minCores, minMemory, minStorage, maxMonthlyCost, region });
  };

  return (
    <Card className="shadow-card">
      <fieldset disabled={isLoading} className="group">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-foreground">
            <Wrench className="h-5 w-5 text-primary" />
            Build Your Bare Metal Machine
            {isLoading && (
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6 group-disabled:opacity-50">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div className="space-y-2">
              <Label htmlFor="min-cores">Min Cores</Label>
              <Input
                id="min-cores"
                type="number"
                placeholder="e.g., 8"
                value={minCores}
                onChange={(e) => setMinCores(e.target.value)}
                className="bg-background"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="min-memory-bm">Min Memory (GB)</Label>
              <Input
                id="min-memory-bm"
                type="number"
                placeholder="e.g., 32"
                value={minMemory}
                onChange={(e) => setMinMemory(e.target.value)}
                className="bg-background"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="min-storage">Min Storage (GB)</Label>
              <Input
                id="min-storage"
                type="number"
                placeholder="e.g., 512"
                value={minStorage}
                onChange={(e) => setMinStorage(e.target.value)}
                className="bg-background"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="max-monthly">Max Monthly Cost</Label>
              <Input
                id="max-monthly"
                type="number"
                placeholder="e.g., 120"
                value={maxMonthlyCost}
                onChange={(e) => setMaxMonthlyCost(e.target.value)}
                className="bg-background"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="bm-region">Location</Label>
              <select
                id="bm-region"
                className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                value={region}
                onChange={(e) => setRegion(e.target.value)}
              >
                <option value="">Any</option>
                {regions.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <Button
            onClick={handleSearch}
            className="w-full md:w-auto bg-gradient-primary hover:shadow-hover transition-all duration-200"
          >
            <Search className="h-4 w-4 mr-2" />
            Find Bare Metal Servers
          </Button>
        </CardContent>
      </fieldset>
    </Card>
  );
};
