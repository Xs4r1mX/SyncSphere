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
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { SelectField } from '@/components/ui/select';
import { ROOT_ID } from '../constants/fileTypes';

export function CopyFileDialog({
  open,
  onOpenChange,
  item,
  folderOptions,
  onSubmit,
  isSubmitting,
}) {
  const [name, setName] = useState('');
  const [parentId, setParentId] = useState(ROOT_ID);

  useEffect(() => {
    if (open && item) {
      setName(`${item.name}${item.is_folder ? '' : ' (copy)'}`);
      setParentId(item.parent_id ?? ROOT_ID);
    }
  }, [open, item]);

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit({ name: name.trim(), parentId });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Copy {item?.is_folder ? 'folder' : 'file'}</DialogTitle>
            <DialogDescription>
              Choose a destination and name for the copy.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-2">
            <div className="grid gap-2">
              <Label htmlFor="copy-name">Name</Label>
              <Input
                id="copy-name"
                value={name}
                onChange={(event) => setName(event.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="copy-destination">Destination folder</Label>
              <SelectField
                id="copy-destination"
                value={parentId}
                onValueChange={setParentId}
                options={folderOptions.map((folder) => ({
                  value: folder.provider_item_id,
                  label: folder.name,
                }))}
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={!name.trim() || isSubmitting}>
              {isSubmitting ? 'Copying…' : 'Copy'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
