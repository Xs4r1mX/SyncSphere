import { FolderOpen, Trash2 } from 'lucide-react';

export function FileExplorerEmpty({ showTrashed }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 px-6 py-16 text-center">
      <div className="flex size-12 items-center justify-center rounded-full border border-border bg-muted">
        {showTrashed ? (
          <Trash2 className="size-5 text-muted-foreground" />
        ) : (
          <FolderOpen className="size-5 text-muted-foreground" />
        )}
      </div>
      <div className="grid gap-1">
        <p className="font-medium">
          {showTrashed ? 'Trash is empty' : 'This folder is empty'}
        </p>
        <p className="max-w-sm text-sm text-muted-foreground">
          {showTrashed
            ? 'Deleted files and folders will appear here.'
            : 'Upload files or create a folder to get started.'}
        </p>
      </div>
    </div>
  );
}
