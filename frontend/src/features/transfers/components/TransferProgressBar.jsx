import { getTransferProgressPercent } from '../utils/progress';

export function TransferProgressBar({ job }) {
  const percent = getTransferProgressPercent(job);
  const itemsLabel =
    job.items_total > 0
      ? `${job.items_completed}/${job.items_total} items`
      : null;

  return (
    <div className="grid min-w-28 gap-1">
      <div className="h-1.5 overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-primary transition-all"
          style={{ width: `${percent}%` }}
        />
      </div>
      <p className="text-xs text-muted-foreground">
        {percent}%{itemsLabel ? ` · ${itemsLabel}` : ''}
      </p>
    </div>
  );
}
