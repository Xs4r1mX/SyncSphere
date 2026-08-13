import { Check, X } from 'lucide-react';

import { cn } from '@/lib/utils';
import { getActivityIcon } from '../constants/actions';
import {
  formatActivityClock,
  formatActivityDescription,
  formatActivityTitle,
  formatProviderLabel,
  formatResourceType,
} from '../utils/formatActivity';

function MetaLine({ ok, label }) {
  return (
    <div className="flex items-center gap-2 text-[13px] text-muted-foreground">
      {ok ? (
        <Check className="size-3.5 shrink-0 text-emerald-500" strokeWidth={2.5} />
      ) : (
        <X className="size-3.5 shrink-0 text-destructive" strokeWidth={2.5} />
      )}
      <span>{label}</span>
    </div>
  );
}

export function ActivityTimelineItem({ entry, isLast, onSelect }) {
  const Icon = getActivityIcon(entry.action, entry.resource_type);
  const failed = entry.status === 'failed';
  const title = formatActivityTitle(entry);

  return (
    <article
      className={cn(
        'grid grid-cols-[3.25rem_2.25rem_minmax(0,1fr)] gap-x-2 sm:grid-cols-[4.75rem_2.25rem_minmax(0,1fr)] sm:gap-x-3',
        !isLast && 'pb-10',
      )}
    >
      <div className="pt-2.5 text-right text-xs text-muted-foreground tabular-nums">
        {formatActivityClock(entry.created_at)}
      </div>

      <div className="relative flex flex-col items-center">
        <div
          className={cn(
            'relative z-10 flex size-9 shrink-0 items-center justify-center rounded-full border-2 bg-card',
            failed
              ? 'border-destructive text-destructive shadow-[0_0_12px_rgba(239,68,68,0.35)]'
              : 'border-emerald-500 text-emerald-400 shadow-[0_0_14px_rgba(16,185,129,0.45)]',
          )}
        >
          <Icon className="size-4" />
        </div>

        {/* spine */}
        <div
          className={cn(
            'absolute top-9 left-1/2 w-px -translate-x-1/2 bg-border',
            isLast ? 'bottom-2' : 'bottom-0',
          )}
        />

        {/* branch node on spine → card */}
        <div
          className={cn(
            'absolute top-[2.7rem] left-1/2 z-10 size-2.5 -translate-x-1/2 rounded-full',
            failed ? 'bg-destructive' : 'bg-emerald-500',
          )}
        />
        <div className="absolute top-[2.9rem] left-1/2 z-0 h-px w-5 bg-border sm:w-6" />
      </div>

      <div className="min-w-0">
        <button
          type="button"
          onClick={() => onSelect?.(entry)}
          className="group w-full rounded-lg text-left outline-none focus-visible:ring-2 focus-visible:ring-ring"
          aria-label={`View details for ${title}`}
        >
          <h3 className="pt-2 text-[15px] font-semibold tracking-tight text-foreground group-hover:underline">
            {title}
          </h3>

          <div
            className={cn(
              'mt-3 overflow-hidden rounded-lg border border-border/60 bg-background/60 transition-colors group-hover:bg-muted/40',
              failed
                ? 'border-l-[3px] border-l-destructive'
                : 'border-l-[3px] border-l-emerald-500',
            )}
          >
            <div className="px-4 py-3">
              <p className="text-sm font-medium text-foreground">
                {formatActivityDescription(entry)}
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                {failed
                  ? 'Event completed with errors.'
                  : 'Event completed successfully.'}
              </p>
            </div>
          </div>

          <div className="mt-3 grid gap-2">
            <MetaLine
              ok={!failed}
              label={`${formatResourceType(entry.resource_type)} resource`}
            />
            {entry.provider ? (
              <MetaLine
                ok={!failed}
                label={`Provider · ${formatProviderLabel(entry.provider)}`}
              />
            ) : null}
            {entry.resource_name ? (
              <MetaLine ok={!failed} label={entry.resource_name} />
            ) : null}
          </div>
        </button>
      </div>
    </article>
  );
}
