import { Link, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

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
import { Skeleton } from '@/components/ui/skeleton';
import { useCloudConnections } from '@/features/cloud/hooks/useCloudConnections';
import { formatConnectionLabel } from '@/features/cloud/utils/formatConnectionLabel';
import { formatFileDate } from '@/features/files/utils/formatFileDate';
import { formatFileSize } from '@/features/files/utils/formatFileSize';
import { TransferProgressBar } from '../components/TransferProgressBar';
import { TransferStatusBadge } from '../components/TransferStatusBadge';
import {
  formatOperationLabel,
  formatStatusLabel,
  isInFlightStatus,
} from '../constants/status';
import { useTransfer, useTransferItems } from '../hooks/useTransfer';
import { useCancelTransfer } from '../hooks/useTransferMutations';

function connectionLabel(connections, uuid) {
  const connection = connections.find((item) => item.uuid === uuid);
  return formatConnectionLabel(connection);
}

export function TransferDetailPage() {
  const { jobUuid } = useParams();
  const jobQuery = useTransfer(jobUuid);
  const itemsQuery = useTransferItems(jobUuid, {
    poll: isInFlightStatus(jobQuery.data?.status),
  });
  const connectionsQuery = useCloudConnections();
  const cancelTransfer = useCancelTransfer();

  const connections = connectionsQuery.data ?? [];
  const job = jobQuery.data;
  const items = itemsQuery.data ?? [];

  if (jobQuery.isLoading) {
    return (
      <div className="grid gap-6">
        <PageHeader title="Transfer" description="Loading job details…" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  if (jobQuery.isError || !job) {
    return (
      <div className="grid gap-6">
        <PageHeader title="Transfer" description="This transfer could not be found." />
        <Alert variant="destructive">
          <AlertDescription>
            {jobQuery.error?.message || 'Transfer job not found.'}
          </AlertDescription>
        </Alert>
        <div>
          <Button render={<Link to={PATHS.TRANSFER_HISTORY} />} variant="outline">
            <ArrowLeft />
            Back to transfers
          </Button>
        </div>
      </div>
    );
  }

  const canCancel = isInFlightStatus(job.status) && !job.cancel_requested;

  return (
    <div className="grid gap-6">
      <PageHeader
        title={job.source_item_name || 'Transfer'}
        description={`${formatOperationLabel(job.operation)} · ${connectionLabel(connections, job.source_connection_uuid)} → ${connectionLabel(connections, job.dest_connection_uuid)}`}
        action={
          <div className="flex flex-wrap gap-2">
            {canCancel ? (
              <Button
                variant="destructive"
                disabled={cancelTransfer.isPending}
                onClick={() => cancelTransfer.mutate(job.uuid)}
              >
                Cancel transfer
              </Button>
            ) : null}
            <Button render={<Link to={PATHS.TRANSFER_HISTORY} />} variant="outline">
              <ArrowLeft />
              Back to transfers
            </Button>
          </div>
        }
      />

      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="grid gap-1">
              <CardTitle>Progress</CardTitle>
              <CardDescription>
                Started {formatFileDate(job.started_at || job.created_at)}
                {job.finished_at ? ` · Finished ${formatFileDate(job.finished_at)}` : ''}
              </CardDescription>
            </div>
            <TransferStatusBadge status={job.status} />
          </div>
        </CardHeader>
        <CardContent className="grid gap-4">
          <TransferProgressBar job={job} />
          <dl className="grid gap-3 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-muted-foreground">Bytes</dt>
              <dd>
                {formatFileSize(job.bytes_transferred)} / {formatFileSize(job.total_bytes)}
              </dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Conflict policy</dt>
              <dd>{formatStatusLabel(job.conflict_policy)}</dd>
            </div>
          </dl>
          {job.error_message ? (
            <Alert variant="destructive">
              <AlertDescription>{job.error_message}</AlertDescription>
            </Alert>
          ) : null}
          {job.cancel_requested && isInFlightStatus(job.status) ? (
            <p className="text-sm text-muted-foreground">
              Cancellation requested. The job will stop after the current item.
            </p>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Items</CardTitle>
          <CardDescription>Per-file status for this transfer job.</CardDescription>
        </CardHeader>
        <CardContent className="overflow-x-auto p-0">
          {itemsQuery.isError ? (
            <div className="p-6">
              <Alert variant="destructive">
                <AlertDescription>
                  {itemsQuery.error.message || 'Could not load transfer items.'}
                </AlertDescription>
              </Alert>
            </div>
          ) : itemsQuery.isLoading ? (
            <div className="grid gap-3 p-6">
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-8 w-full" />
            </div>
          ) : items.length === 0 ? (
            <p className="px-6 py-8 text-sm text-muted-foreground">
              Items will appear once planning completes.
            </p>
          ) : (
            <table className="w-full min-w-[640px] text-sm">
              <thead>
                <tr className="border-b border-border text-left text-muted-foreground">
                  <th className="px-6 py-3 font-medium">Name</th>
                  <th className="px-6 py-3 font-medium">Type</th>
                  <th className="px-6 py-3 font-medium">Size</th>
                  <th className="px-6 py-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.uuid} className="border-b border-border/60 last:border-0">
                    <td className="px-6 py-3">
                      <div className="grid gap-0.5">
                        <span className="font-medium">{item.source_name}</span>
                        {item.source_path ? (
                          <span className="text-xs text-muted-foreground">
                            {item.source_path}
                          </span>
                        ) : null}
                      </div>
                    </td>
                    <td className="px-6 py-3 text-muted-foreground">
                      {formatStatusLabel(item.kind)}
                    </td>
                    <td className="px-6 py-3 text-muted-foreground">
                      {item.kind === 'folder' ? '—' : formatFileSize(item.size_bytes)}
                    </td>
                    <td className="px-6 py-3">
                      <TransferStatusBadge status={item.status} />
                      {item.error_message ? (
                        <p className="mt-1 text-xs text-destructive">{item.error_message}</p>
                      ) : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
