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
import { SelectField } from '@/components/ui/select';
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
            <SelectField
              id="move-destination"
              value={parentId}
              onValueChange={setParentId}
              options={folderOptions.map((folder) => ({
                value: folder.provider_item_id,
                label: folder.name,
              }))}
            />
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
