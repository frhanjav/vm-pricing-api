import { Server, Search } from "lucide-react";

export const Header = () => {
  return (
    <header className="bg-gradient-header border-b border-border h-header sticky top-0 z-50 backdrop-blur-sm">
      <div className="container mx-auto max-w-content px-6 h-full flex items-center">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Server className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-foreground">
              Virtual Machine Finder
            </h1>
            <p className="text-sm text-muted-foreground">
              Compare cloud and bare metal instances across providers
            </p>
          </div>
        </div>
      </div>
    </header>
  );
};
