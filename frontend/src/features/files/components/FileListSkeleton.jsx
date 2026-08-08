import { Skeleton } from '@/components/ui/skeleton';

export function FileListSkeleton() {
  return (
    <div className="grid gap-0">
      {[0, 1, 2, 3, 4].map((row) => (
        <div
          key={row}
          className="flex items-center gap-4 border-b border-border px-6 py-4 last:border-b-0"
        >
          <Skeleton className="size-5 shrink-0 rounded" />
          <Skeleton className="h-4 flex-1 max-w-xs" />
          <Skeleton className="hidden h-4 w-16 sm:block" />
          <Skeleton className="hidden h-4 w-24 md:block" />
          <Skeleton className="size-8 shrink-0 rounded-md" />
        </div>
      ))}
    </div>
  );
}
