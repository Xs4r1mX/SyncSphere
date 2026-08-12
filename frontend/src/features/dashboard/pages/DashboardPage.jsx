import { Link } from 'react-router-dom';
import {
  Activity,
  ArrowLeftRight,
  Cloud,
  HardDrive,
} from 'lucide-react';

import { PageHeader } from '@/components/layout/PageHeader';
import { PATHS } from '@/app/routes/paths';
import { useAuth } from '@/features/auth';
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
import { formatQuotaLabel } from '@/features/cloud/utils/formatQuota';
import { formatFileDate } from '@/features/files/utils/formatFileDate';
import { TransferStatusBadge } from '@/features/transfers/components/TransferStatusBadge';
import {
  formatOperationLabel,
  isInFlightStatus,
} from '@/features/transfers/constants/status';
import { useTransfers } from '@/features/transfers/hooks/useTransfers';

function StatCard({ label, value, icon: Icon, isLoading }) {
  return (
    <Card size="sm">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {label}
        </CardTitle>
        <Icon className="size-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <Skeleton className="h-8 w-16" />
        ) : (
          <p className="text-2xl font-semibold">{value}</p>
        )}
      </CardContent>
    </Card>
  );
}

export function DashboardPage() {
  const { user } = useAuth();
  const connectionsQuery = useCloudConnections();
  const transfersQuery = useTransfers();

  const connections = connectionsQuery.data ?? [];
  const transfers = transfersQuery.data ?? [];
  const isLoading = connectionsQuery.isLoading || transfersQuery.isLoading;

  const activeTransfers = transfers.filter((job) => isInFlightStatus(job.status)).length;
  const usedBytes = connections.reduce(
    (sum, connection) => sum + (connection.quota_used_bytes ?? 0),
    0,
  );
  const totalBytes = connections.reduce(
    (sum, connection) => sum + (connection.quota_total_bytes ?? 0),
    0,
  );
  const hasQuota = connections.some(
    (connection) =>
      connection.quota_used_bytes != null || connection.quota_total_bytes != null,
  );
  const recentTransfers = transfers.slice(0, 5);

  return (
    <div className="grid gap-6">
      <PageHeader
        title={`Welcome${user?.first_name ? `, ${user.first_name}` : ''}`}
        description="Your cloud storage workspace overview."
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Cloud Connections"
          value={String(connections.length)}
          icon={Cloud}
          isLoading={connectionsQuery.isLoading}
        />
        <StatCard
          label="Active Transfers"
          value={String(activeTransfers)}
          icon={ArrowLeftRight}
          isLoading={transfersQuery.isLoading}
        />
        <StatCard
          label="Storage Used"
          value={hasQuota ? formatQuotaLabel(usedBytes, totalBytes || null) : '—'}
          icon={HardDrive}
          isLoading={connectionsQuery.isLoading}
        />
        <StatCard
          label="Transfers"
          value={String(transfers.length)}
          icon={Activity}
          isLoading={transfersQuery.isLoading}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Quick actions</CardTitle>
            <CardDescription>
              Jump to common tasks across your workspace.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            <Button render={<Link to={PATHS.CLOUD_STORAGES} />} variant="secondary">
              <Cloud />
              Manage cloud storages
            </Button>
            <Button render={<Link to={PATHS.TRANSFER_HISTORY} />} variant="secondary">
              <ArrowLeftRight />
              View transfer history
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent transfers</CardTitle>
            <CardDescription>
              Latest copy and move jobs across your connected storages.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3">
            {isLoading ? (
              <>
                <Skeleton className="h-14 w-full" />
                <Skeleton className="h-14 w-full" />
              </>
            ) : recentTransfers.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No transfers yet. Copy or move a file from a connected storage to get started.
              </p>
            ) : (
              recentTransfers.map((job) => (
                <Link
                  key={job.uuid}
                  to={PATHS.transferDetail(job.uuid)}
                  className="flex items-start gap-3 rounded-lg border border-border/60 bg-muted/20 p-3 hover:bg-muted/40"
                >
                  <div className="flex size-8 shrink-0 items-center justify-center rounded-md bg-muted">
                    <ArrowLeftRight className="size-4 text-muted-foreground" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">
                      {formatOperationLabel(job.operation)} — {job.source_item_name || 'Untitled'}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {formatFileDate(job.created_at)}
                    </p>
                  </div>
                  <TransferStatusBadge status={job.status} />
                </Link>
              ))
            )}
            <Button render={<Link to={PATHS.TRANSFER_HISTORY} />} variant="ghost" className="justify-start px-0">
              <ArrowLeftRight />
              View all transfers
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Storage overview</CardTitle>
          <CardDescription>
            A snapshot of usage across connected providers.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {connectionsQuery.isLoading ? (
            <Skeleton className="h-16 w-full" />
          ) : connections.length === 0 ? (
            <div className="flex items-center gap-4 text-muted-foreground">
              <HardDrive className="size-8 shrink-0" />
              <p className="text-sm">
                Connect cloud storages to see usage breakdowns and quota details here.
              </p>
            </div>
          ) : (
            <div className="grid gap-4">
              {connections.map((connection) => (
                <div key={connection.uuid} className="grid gap-1.5">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">
                      {connection.display_name || connection.provider_label}
                    </span>
                    <span className="text-muted-foreground">
                      {formatQuotaLabel(
                        connection.quota_used_bytes,
                        connection.quota_total_bytes,
                      )}
                    </span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-muted">
                    <div
                      className="h-full rounded-full bg-primary"
                      style={{
                        width: `${
                          connection.quota_total_bytes
                            ? Math.min(
                                Math.round(
                                  ((connection.quota_used_bytes ?? 0) /
                                    connection.quota_total_bytes) *
                                    100,
                                ),
                                100,
                              )
                            : 0
                        }%`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
