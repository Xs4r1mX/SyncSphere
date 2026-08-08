import {
  formatQuotaLabel,
  getQuotaPercentage,
} from '@/features/cloud/utils/formatQuota';

export function FileQuotaSummary({ connection }) {
  const percentage = getQuotaPercentage(
    connection.quota_used_bytes,
    connection.quota_total_bytes,
  );

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="grid gap-1.5">
        <div className="flex items-center justify-between text-sm">
          <span className="font-medium">Storage used</span>
          <span className="text-muted-foreground">
            {formatQuotaLabel(
              connection.quota_used_bytes,
              connection.quota_total_bytes,
            )}
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
