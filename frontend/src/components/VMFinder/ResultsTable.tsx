import React from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ChevronLeft,
  ChevronRight,
  Database,
  Loader2,
  AlertTriangle,
} from "lucide-react";
import { VMInstance } from "@/types";

interface ResultsTableProps {
  instances: VMInstance[];
  isLoading: boolean;
  isError: boolean;
  currentPage: number;
  totalPages: number;
  totalResults: number;
  onPageChange: (page: number) => void;
}

export const ResultsTable: React.FC<ResultsTableProps> = ({
  instances,
  isLoading,
  isError,
  currentPage,
  totalPages,
  totalResults,
  onPageChange,
}) => {
  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency,
      minimumFractionDigits: 4,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const renderTableContent = () => {
    if (isLoading) {
      return (
        <TableRow>
          <TableCell colSpan={9} className="h-48 text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
          </TableCell>
        </TableRow>
      );
    }

    if (isError) {
      return (
        <TableRow>
          <TableCell colSpan={9} className="h-48 text-center text-destructive">
            <AlertTriangle className="h-8 w-8 mx-auto mb-2" />
            Failed to load data. Please try again.
          </TableCell>
        </TableRow>
      );
    }

    if (instances.length === 0) {
      return (
        <TableRow>
          <TableCell
            colSpan={9}
            className="h-48 text-center text-muted-foreground"
          >
            No results found.
          </TableCell>
        </TableRow>
      );
    }

    return instances.map((vm) => (
      <TableRow
        key={vm.id}
        className="border-border hover:bg-muted/40 transition-colors"
      >
        <TableCell className="font-mono text-primary font-medium">
          {vm.instance_name}
        </TableCell>
        <TableCell>{vm.provider}</TableCell>
        <TableCell className="font-mono text-muted-foreground">
          {vm.region}
        </TableCell>
        <TableCell className="text-right">{vm.vcpus}</TableCell>
        <TableCell className="text-right">{vm.memory_gb}</TableCell>
        <TableCell className="text-right font-medium">
          {vm.hourly_cost
            ? formatCurrency(vm.hourly_cost, vm.currency || "USD")
            : "N/A"}
        </TableCell>
        <TableCell className="text-right font-medium">
          {vm.monthly_cost
            ? formatCurrency(vm.monthly_cost, vm.currency || "USD")
            : "N/A"}
        </TableCell>
        <TableCell>
          <span className="px-2 py-1 bg-secondary rounded text-xs font-medium">
            {vm.instance_family || "N/A"}
          </span>
        </TableCell>
        <TableCell className="text-muted-foreground text-sm">
          {formatDate(vm.last_updated)}
        </TableCell>
      </TableRow>
    ));
  };

  return (
    <Card className="shadow-card">
      <CardHeader>
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <CardTitle className="flex items-center gap-2 text-foreground">
            <Database className="h-5 w-5 text-primary" />
            Results
          </CardTitle>
          <div className="text-sm text-muted-foreground">
            Page {currentPage} of {totalPages} ({totalResults} total results)
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-border">
                <TableHead className="font-semibold text-foreground">
                  Instance
                </TableHead>
                <TableHead className="font-semibold text-foreground">
                  Provider
                </TableHead>
                <TableHead className="font-semibold text-foreground">
                  Region
                </TableHead>
                <TableHead className="font-semibold text-foreground text-right">
                  vCPUs
                </TableHead>
                <TableHead className="font-semibold text-foreground text-right">
                  Mem (GB)
                </TableHead>
                <TableHead className="font-semibold text-foreground text-right">
                  Hourly Cost
                </TableHead>
                <TableHead className="font-semibold text-foreground text-right">
                  Monthly Cost
                </TableHead>
                <TableHead className="font-semibold text-foreground">
                  Family
                </TableHead>
                <TableHead className="font-semibold text-foreground">
                  Last Updated
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>{renderTableContent()}</TableBody>
          </Table>
        </div>

        <div className="flex items-center justify-between mt-6">
          <Button
            variant="outline"
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1 || isLoading}
            className="flex items-center gap-2"
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </Button>

          <Button
            variant="outline"
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages || isLoading}
            className="flex items-center gap-2"
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
