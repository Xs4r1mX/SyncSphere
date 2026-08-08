import {
  Copy,
  Download,
  ExternalLink,
  FolderInput,
  MoreHorizontal,
  Pencil,
  RotateCcw,
  Trash2,
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export function FileRowActions({
  item,
  showTrashed,
  onRename,
  onDelete,
  onRestore,
  onCopy,
  onDownload,
  onMove,
}) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        render={
          <Button variant="ghost" size="icon-sm" aria-label={`Actions for ${item.name}`} />
        }
      >
        <MoreHorizontal />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {!showTrashed && item.web_view_link ? (
          <DropdownMenuItem
            onClick={() => window.open(item.web_view_link, '_blank', 'noopener,noreferrer')}
          >
            <ExternalLink />
            Open
          </DropdownMenuItem>
        ) : null}

        {!showTrashed && !item.is_folder ? (
          <DropdownMenuItem onClick={onDownload}>
            <Download />
            Download
          </DropdownMenuItem>
        ) : null}

        {!showTrashed ? (
          <>
            <DropdownMenuItem onClick={() => onRename(item)}>
              <Pencil />
              Rename
            </DropdownMenuItem>
            <DropdownMenuItem onClick={onMove}>
              <FolderInput />
              Move
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onCopy(item)}>
              <Copy />
              Copy
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem variant="destructive" onClick={() => onDelete(item)}>
              <Trash2 />
              Move to trash
            </DropdownMenuItem>
          </>
        ) : (
          <DropdownMenuItem onClick={() => onRestore(item.provider_item_id)}>
            <RotateCcw />
            Restore
          </DropdownMenuItem>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
