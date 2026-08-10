import { useEffect, useState } from 'react';

import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { ROOT_ID } from '../constants/fileTypes';

export function MoveFileDialog({
  open,
  onOpenChange,
  item,
  folderOptions,
  onSubmit,
  isSubmitting,
}) {
  const [parentId, setParentId] = useState(ROOT_ID);

  useEffect(() => {
    if (open && item) {
      setParentId(item.parent_id ?? ROOT_ID);
    }
  }, [open, item]);

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit({ parentId });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Move {item?.is_folder ? 'folder' : 'file'}</DialogTitle>
            <DialogDescription>
              Choose a destination folder for &ldquo;{item?.name}&rdquo;.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-2 py-2">
            <Label htmlFor="move-destination">Destination folder</Label>
            <select
              id="move-destination"
              className="h-9 rounded-md border border-input bg-background px-3 text-sm text-foreground"
              value={parentId}
              onChange={(event) => setParentId(event.target.value)}
            >
              {folderOptions.map((folder) => (
                <option key={folder.provider_item_id} value={folder.provider_item_id}>
                  {folder.name}
                </option>
              ))}
            </select>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Moving…' : 'Move'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
