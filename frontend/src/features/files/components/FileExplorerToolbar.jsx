import { useRef } from 'react';
import { ArrowLeftRight, FolderPlus, Trash2, Upload } from 'lucide-react';

import { Button } from '@/components/ui/button';

export function FileExplorerToolbar({
  showTrashed,
  trashSupported = true,
  isUploading,
  onToggleTrashed,
  onCreateFolder,
  onUpload,
  onMigrate,
}) {
  const fileInputRef = useRef(null);

  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex flex-wrap gap-2">
        <Button
          variant="secondary"
          disabled={showTrashed || isUploading}
          onClick={() => fileInputRef.current?.click()}
        >
          <Upload />
          {isUploading ? 'Uploading…' : 'Upload'}
        </Button>
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          onChange={(event) => {
            const file = event.target.files?.[0];

            if (file) {
              onUpload(file);
            }

            if (fileInputRef.current) {
              fileInputRef.current.value = '';
            }
          }}
        />
        <Button
          variant="secondary"
          disabled={showTrashed}
          onClick={onCreateFolder}
        >
          <FolderPlus />
          New folder
        </Button>
        {onMigrate ? (
          <Button variant="secondary" disabled={showTrashed} onClick={onMigrate}>
            <ArrowLeftRight />
            Migrate drive
          </Button>
        ) : null}
      </div>

      {trashSupported ? (
        <Button
          variant={showTrashed ? 'default' : 'outline'}
          onClick={() => onToggleTrashed(!showTrashed)}
        >
          <Trash2 />
          {showTrashed ? 'Viewing trash' : 'Trash'}
        </Button>
      ) : null}
    </div>
  );
}
