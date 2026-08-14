import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { formatFileDate } from '../utils/formatFileDate';
import { formatFileSize } from '../utils/formatFileSize';
import { getFileIcon } from '../utils/getFileIcon';
import { FileExplorerEmpty } from './FileExplorerEmpty';
import { FileListSkeleton } from './FileListSkeleton';
import { FileRowActions } from './FileRowActions';

export function FileListTable({
  items,
  isLoading,
  showTrashed,
  onOpenFolder,
  onRename,
  onDelete,
  onRestore,
  onCopy,
  onOpen,
  onDownload,
  onMove,
  onTransfer,
  onPermanentDelete,
}) {
  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-0">
          <FileListSkeleton />
        </CardContent>
      </Card>
    );
  }

  if (items.length === 0) {
    return (
      <Card>
        <CardContent className="p-0">
          <FileExplorerEmpty showTrashed={showTrashed} />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent className="overflow-x-auto p-0">
        <table className="w-full min-w-[640px] text-sm">
          <thead>
            <tr className="border-b border-border text-left text-muted-foreground">
              <th className="px-6 py-3 font-medium">Name</th>
              <th className="hidden px-6 py-3 font-medium sm:table-cell">Size</th>
              <th className="hidden px-6 py-3 font-medium md:table-cell">Modified</th>
              <th className="px-6 py-3 font-medium">
                <span className="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => {
              const Icon = getFileIcon(item);

              return (
                <tr
                  key={item.provider_item_id}
                  className={cn(
                    'border-b border-border last:border-b-0',
                    item.is_folder && !showTrashed && 'cursor-pointer hover:bg-muted/50',
                  )}
                  onClick={() => {
                    if (item.is_folder && !showTrashed) {
                      onOpenFolder(item.provider_item_id);
                    }
                  }}
                >
                  <td className="px-6 py-3">
                    <div className="flex items-center gap-3">
                      <Icon
                        className={cn(
                          'size-4 shrink-0',
                          item.is_folder ? 'text-primary' : 'text-muted-foreground',
                        )}
                      />
                      <span className="truncate font-medium">{item.name}</span>
                    </div>
                  </td>
                  <td className="hidden px-6 py-3 text-muted-foreground sm:table-cell">
                    {item.is_folder ? '—' : formatFileSize(item.size)}
                  </td>
                  <td className="hidden px-6 py-3 text-muted-foreground md:table-cell">
                    {formatFileDate(item.modified_at)}
                  </td>
                  <td className="px-6 py-3 text-right">
                    <div onClick={(event) => event.stopPropagation()}>
                      <FileRowActions
                        item={item}
                        showTrashed={showTrashed}
                        onRename={onRename}
                        onDelete={onDelete}
                        onRestore={onRestore}
                        onCopy={onCopy}
                        onOpen={onOpen}
                        onDownload={onDownload}
                        onMove={onMove}
                        onTransfer={onTransfer}
                        onPermanentDelete={onPermanentDelete}
                      />
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
}
