import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Skeleton } from '@/components/ui/skeleton';
import { formatFileDate } from '@/features/files/utils/formatFileDate';
import { getActivityIcon } from '../constants/actions';
import { useActivityDetail } from '../hooks/useActivity';
import {
  formatActivityTitle,
  formatProviderLabel,
  formatResourceType,
} from '../utils/formatActivity';

function DetailRow({ label, children }) {
  return (
    <div className="grid gap-1 sm:grid-cols-[140px_1fr] sm:items-start sm:gap-4">
      <dt className="text-sm text-muted-foreground">{label}</dt>
      <dd className="text-sm break-words">{children}</dd>
    </div>
  );
}

function formatMetadata(metadata) {
  if (metadata == null) {
    return null;
  }
  if (typeof metadata === 'string') {
    return metadata;
  }
  if (typeof metadata === 'object' && Object.keys(metadata).length === 0) {
    return null;
  }
  try {
    return JSON.stringify(metadata, null, 2);
  } catch {
    return String(metadata);
  }
}

export function ActivityDetailDialog({ open, onOpenChange, activityUuid }) {
  const detailQuery = useActivityDetail(activityUuid, { enabled: open });
  const entry = detailQuery.data;
  const Icon = entry
    ? getActivityIcon(entry.action, entry.resource_type)
    : null;
  const metadataText = entry ? formatMetadata(entry.metadata) : null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 pr-8">
            {Icon ? (
              <span className="flex size-8 shrink-0 items-center justify-center rounded-md bg-muted">
                <Icon className="size-4 text-muted-foreground" />
              </span>
            ) : null}
            <span className="truncate">
              {entry ? formatActivityTitle(entry) : 'Activity details'}
            </span>
          </DialogTitle>
          <DialogDescription>
            Full details for this workspace event.
          </DialogDescription>
        </DialogHeader>

        {detailQuery.isLoading ? (
          <div className="grid gap-3 py-2">
            <Skeleton className="h-4 w-2/3" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-1/2" />
            <Skeleton className="h-20 w-full" />
          </div>
        ) : detailQuery.isError ? (
          <Alert variant="destructive">
            <AlertDescription>
              {detailQuery.error.message || 'Could not load activity details.'}
            </AlertDescription>
          </Alert>
        ) : entry ? (
          <dl className="grid gap-3 py-1">
            <DetailRow label="Status">
              <Badge variant={entry.status === 'failed' ? 'destructive' : 'success'}>
                {entry.status === 'failed' ? 'Failed' : 'Success'}
              </Badge>
            </DetailRow>
            <DetailRow label="Action">{entry.action || '—'}</DetailRow>
            <DetailRow label="Resource">
              {entry.resource_name || '—'}
            </DetailRow>
            <DetailRow label="Resource type">
              {formatResourceType(entry.resource_type)}
            </DetailRow>
            <DetailRow label="Resource ID">
              <span className="font-mono text-xs">{entry.resource_id || '—'}</span>
            </DetailRow>
            <DetailRow label="Provider">
              <span className="capitalize">{formatProviderLabel(entry.provider)}</span>
            </DetailRow>
            <DetailRow label="Connection">
              <span className="font-mono text-xs">
                {entry.connection_uuid || '—'}
              </span>
            </DetailRow>
            <DetailRow label="Request ID">
              <span className="font-mono text-xs">{entry.request_id || '—'}</span>
            </DetailRow>
            <DetailRow label="Created">
              {formatFileDate(entry.created_at)}
            </DetailRow>
            <DetailRow label="Updated">
              {formatFileDate(entry.updated_at)}
            </DetailRow>
            {metadataText ? (
              <DetailRow label="Metadata">
                <pre className="max-h-40 overflow-auto rounded-md bg-muted/50 p-3 font-mono text-xs whitespace-pre-wrap">
                  {metadataText}
                </pre>
              </DetailRow>
            ) : null}
          </dl>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}
