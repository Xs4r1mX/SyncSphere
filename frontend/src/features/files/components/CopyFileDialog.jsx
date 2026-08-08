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
import { getFolderOptions } from '../data/mockFileExplorer';
import { ROOT_ID } from '../constants/fileTypes';

export function CopyFileDialog({ open, onOpenChange, item, allItems, onSubmit }) {
  const [name, setName] = useState('');
  const [parentId, setParentId] = useState(ROOT_ID);

  const folderOptions = [
    { provider_item_id: ROOT_ID, name: 'My Drive' },
    ...getFolderOptions(allItems).map((folder) => ({
      provider_item_id: folder.provider_item_id,
      name: folder.name,
    })),
  ];

  useEffect(() => {
    if (open && item) {
      setName(`${item.name}${item.is_folder ? '' : ' (copy)'}`);
      setParentId(item.parent_id ?? ROOT_ID);
    }
  }, [open, item]);

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit();
    onOpenChange(false);
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
              <select
                id="copy-destination"
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
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={!name.trim()}>
              Copy
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
