import {
  formatQuotaLabel,
  getQuotaPercentage,
} from '@/features/cloud/utils/formatQuota';

export function FileQuotaSummary({ quotaUsedBytes, quotaTotalBytes, isLoading }) {
  if (isLoading) {
    return (
      <div className="rounded-lg border border-border bg-card p-4">
        <div className="h-2 animate-pulse rounded-full bg-muted" />
      </div>
    );
  }

  const percentage = getQuotaPercentage(quotaUsedBytes, quotaTotalBytes);
  const hasQuota = quotaUsedBytes != null || quotaTotalBytes != null;

  if (!hasQuota) {
    return (
      <div className="rounded-lg border border-border bg-card p-4">
        <p className="text-sm text-muted-foreground">Storage quota unavailable</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="grid gap-1.5">
        <div className="flex items-center justify-between text-sm">
          <span className="font-medium">Storage used</span>
          <span className="text-muted-foreground">
            {formatQuotaLabel(quotaUsedBytes, quotaTotalBytes)}
          </span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-muted">
          <div
            className="h-full rounded-full bg-primary transition-all"
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
    </div>
  );
}
