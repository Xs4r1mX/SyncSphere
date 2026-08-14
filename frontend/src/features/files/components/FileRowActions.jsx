import {
  ArrowLeftRight,
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
  onOpen,
  onDownload,
  onMove,
  onTransfer,
  onPermanentDelete,
}) {
  const handleOpen = () => {
    if (item.web_view_link) {
      window.open(item.web_view_link, '_blank', 'noopener,noreferrer');
      return;
    }
    onOpen(item);
  };

  const canOpen = item.can_open ?? (!item.is_folder || Boolean(item.web_view_link));
  const canDownload = item.can_download ?? !item.is_folder;

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
        {!showTrashed && canOpen ? (
          <DropdownMenuItem onClick={handleOpen}>
            <ExternalLink />
            Open
          </DropdownMenuItem>
        ) : null}

        {!showTrashed && canDownload ? (
          <DropdownMenuItem onClick={() => onDownload(item)}>
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
            <DropdownMenuItem onClick={() => onMove(item)}>
              <FolderInput />
              Move
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onCopy(item)}>
              <Copy />
              Copy
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onTransfer(item)}>
              <ArrowLeftRight />
              Transfer to another cloud
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem variant="destructive" onClick={() => onDelete(item)}>
              <Trash2 />
              Move to trash
            </DropdownMenuItem>
          </>
        ) : (
          <>
            <DropdownMenuItem onClick={() => onRestore(item.provider_item_id)}>
              <RotateCcw />
              Restore
            </DropdownMenuItem>
            <DropdownMenuItem variant="destructive" onClick={() => onPermanentDelete(item)}>
              <Trash2 />
              Delete permanently
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
