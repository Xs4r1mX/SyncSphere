import { Search } from 'lucide-react';

import { PageHeader } from '@/components/layout/PageHeader';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { mockTransfers, statusOptions } from '../data/mockTransfers';

function getStatusVariant(status) {
  switch (status) {
    case 'Completed':
      return 'secondary';
    case 'In Progress':
      return 'outline';
    case 'Failed':
      return 'destructive';
    default:
      return 'outline';
  }
}

export function TransferHistoryPage() {
  return (
    <div className="grid gap-6">
      <PageHeader
        title="Transfer History"
        description="Review past and in-progress file transfers."
      />

      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
          <CardDescription>
            Search and filter transfers. Functionality coming soon.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1">
            <Search className="absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              className="pl-9"
              placeholder="Search transfers..."
              readOnly
              aria-label="Search transfers"
            />
          </div>
          <select
            className="h-9 rounded-md border border-input bg-background px-3 text-sm text-foreground"
            defaultValue="All"
            aria-label="Filter by status"
          >
            {statusOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="overflow-x-auto p-0">
          <table className="w-full min-w-[640px] text-sm">
            <thead>
              <tr className="border-b border-border text-left text-muted-foreground">
                <th className="px-6 py-3 font-medium">Name</th>
                <th className="px-6 py-3 font-medium">Source</th>
                <th className="px-6 py-3 font-medium">Destination</th>
                <th className="px-6 py-3 font-medium">Status</th>
                <th className="px-6 py-3 font-medium">Date</th>
              </tr>
            </thead>
            <tbody>
              {mockTransfers.map((transfer) => (
                <tr key={transfer.id} className="border-b border-border/60 last:border-0">
                  <td className="px-6 py-4 font-medium">{transfer.name}</td>
                  <td className="px-6 py-4 text-muted-foreground">{transfer.source}</td>
                  <td className="px-6 py-4 text-muted-foreground">{transfer.destination}</td>
                  <td className="px-6 py-4">
                    <Badge variant={getStatusVariant(transfer.status)}>
                      {transfer.status}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 text-muted-foreground">{transfer.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
