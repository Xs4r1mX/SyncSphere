import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { Search } from 'lucide-react';

import { PATHS } from '@/app/routes/paths';
import { PageHeader } from '@/components/layout/PageHeader';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { SelectField } from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { useCloudConnections } from '@/features/cloud/hooks/useCloudConnections';
import { formatConnectionLabel } from '@/features/cloud/utils/formatConnectionLabel';
import { formatFileDate } from '@/features/files/utils/formatFileDate';
import { TransferProgressBar } from '../components/TransferProgressBar';
import { TransferStatusBadge } from '../components/TransferStatusBadge';
import {
  formatOperationLabel,
  isInFlightStatus,
  STATUS_FILTER_OPTIONS,
} from '../constants/status';
import { useCancelTransfer } from '../hooks/useTransferMutations';
import { useTransfers } from '../hooks/useTransfers';

function connectionLabel(connections, uuid) {
  const connection = connections.find((item) => item.uuid === uuid);
  return formatConnectionLabel(connection);
}

function TransfersSkeleton() {
  return (
    <Card>
      <CardContent className="grid gap-4 p-6">
        {[0, 1, 2].map((row) => (
          <Skeleton key={row} className="h-10 w-full" />
        ))}
      </CardContent>
    </Card>
  );
}

export function TransferHistoryPage() {
  const [statusFilter, setStatusFilter] = useState('all');
  const [search, setSearch] = useState('');

  const transfersQuery = useTransfers(statusFilter);
  const connectionsQuery = useCloudConnections();
  const cancelTransfer = useCancelTransfer();

  const connections = connectionsQuery.data ?? [];
  const jobs = transfersQuery.data ?? [];

  const filteredJobs = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) {
      return jobs;
    }

    return jobs.filter((job) => {
      const name = job.source_item_name ?? '';
      const operation = formatOperationLabel(job.operation);
      return (
        name.toLowerCase().includes(query) ||
        operation.toLowerCase().includes(query)
      );
    });
  }, [jobs, search]);

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
            Search by file name or filter by job status.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1">
            <Search className="absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              className="pl-9"
              placeholder="Search transfers..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              aria-label="Search transfers"
            />
          </div>
          <SelectField
            className="sm:w-48"
            value={statusFilter}
            onValueChange={setStatusFilter}
            aria-label="Filter by status"
            options={STATUS_FILTER_OPTIONS.map((option) => ({
              value: option.value,
              label: option.label,
            }))}
          />
        </CardContent>
      </Card>

      {transfersQuery.isError ? (
        <Alert variant="destructive">
          <AlertDescription>
            {transfersQuery.error.message || 'Could not load transfers.'}
          </AlertDescription>
        </Alert>
      ) : null}

      {transfersQuery.isLoading ? (
        <TransfersSkeleton />
      ) : filteredJobs.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>No transfers yet</CardTitle>
            <CardDescription>
              Start a copy or move from a connected cloud storage to see jobs here.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button render={<Link to={PATHS.CLOUD_STORAGES} />}>
              Browse cloud storages
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="overflow-x-auto p-0">
            <table className="w-full min-w-[720px] text-sm">
              <thead>
                <tr className="border-b border-border text-left text-muted-foreground">
                  <th className="px-6 py-3 font-medium">Name</th>
                  <th className="px-6 py-3 font-medium">Operation</th>
                  <th className="px-6 py-3 font-medium">Source</th>
                  <th className="px-6 py-3 font-medium">Destination</th>
                  <th className="px-6 py-3 font-medium">Status</th>
                  <th className="px-6 py-3 font-medium">Progress</th>
                  <th className="px-6 py-3 font-medium">Date</th>
                  <th className="px-6 py-3 font-medium">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredJobs.map((job) => (
                  <tr key={job.uuid} className="border-b border-border/60 last:border-0">
                    <td className="px-6 py-4">
                      <Link
                        to={PATHS.transferDetail(job.uuid)}
                        className="font-medium hover:underline"
                      >
                        {job.source_item_name || 'Untitled'}
                      </Link>
                    </td>
                    <td className="px-6 py-4 text-muted-foreground">
                      {formatOperationLabel(job.operation)}
                    </td>
                    <td className="px-6 py-4 text-muted-foreground">
                      {connectionLabel(connections, job.source_connection_uuid)}
                    </td>
                    <td className="px-6 py-4 text-muted-foreground">
                      {connectionLabel(connections, job.dest_connection_uuid)}
                    </td>
                    <td className="px-6 py-4">
                      <TransferStatusBadge status={job.status} />
                    </td>
                    <td className="px-6 py-4">
                      <TransferProgressBar job={job} />
                    </td>
                    <td className="px-6 py-4 text-muted-foreground">
                      {formatFileDate(job.created_at)}
                    </td>
                    <td className="px-6 py-4 text-right">
                      {isInFlightStatus(job.status) && !job.cancel_requested ? (
                        <Button
                          variant="ghost"
                          size="sm"
                          disabled={
                            cancelTransfer.isPending &&
                            cancelTransfer.variables === job.uuid
                          }
                          onClick={() => cancelTransfer.mutate(job.uuid)}
                        >
                          Cancel
                        </Button>
                      ) : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
