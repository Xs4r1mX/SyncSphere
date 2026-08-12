import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { PATHS } from '@/app/routes/paths';
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
import { useCloudConnections } from '@/features/cloud/hooks/useCloudConnections';
import { ROOT_ID } from '@/features/files/constants/fileTypes';
import { useFileList } from '@/features/files/hooks/useFileList';
import { useCreateTransfer } from '../hooks/useTransferMutations';

export function StartTransferDialog({
  open,
  onOpenChange,
  item,
  sourceConnectionUuid,
}) {
  const navigate = useNavigate();
  const connectionsQuery = useCloudConnections();
  const createTransfer = useCreateTransfer();

  const [destConnectionUuid, setDestConnectionUuid] = useState('');
  const [destParentId, setDestParentId] = useState(ROOT_ID);
  const [mode, setMode] = useState('copy');
  const [conflictPolicy, setConflictPolicy] = useState('reject');

  const destFoldersQuery = useFileList(destConnectionUuid, {
    parentId: ROOT_ID,
    trashed: false,
    enabled: open && Boolean(destConnectionUuid),
  });

  const destConnections = useMemo(
    () =>
      (connectionsQuery.data ?? []).filter(
        (connection) =>
          connection.uuid !== sourceConnectionUuid && connection.status === 'active',
      ),
    [connectionsQuery.data, sourceConnectionUuid],
  );

  const destFolders = useMemo(
    () =>
      (destFoldersQuery.data?.pages.flatMap((page) => page.items) ?? []).filter(
        (folder) => folder.is_folder && !folder.trashed,
      ),
    [destFoldersQuery.data],
  );

  useEffect(() => {
    if (!open) {
      return;
    }

    setMode('copy');
    setConflictPolicy('reject');
    setDestParentId(ROOT_ID);
    setDestConnectionUuid(destConnections[0]?.uuid ?? '');
  }, [open, destConnections]);

  const handleSubmit = (event) => {
    event.preventDefault();

    if (!item || !destConnectionUuid) {
      return;
    }

    const operation = item.is_folder
      ? mode === 'move'
        ? 'move_all'
        : 'copy_all'
      : mode;

    createTransfer.mutate(
      {
        operation,
        source_connection_uuid: sourceConnectionUuid,
        dest_connection_uuid: destConnectionUuid,
        source_item_id: item.provider_item_id,
        dest_parent_id: destParentId,
        conflict_policy: conflictPolicy,
      },
      {
        onSuccess: (job) => {
          onOpenChange(false);
          navigate(PATHS.transferDetail(job.uuid));
        },
      },
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Transfer to another cloud</DialogTitle>
            <DialogDescription>
              Copy or move &ldquo;{item?.name}&rdquo; to a different connected storage.
            </DialogDescription>
          </DialogHeader>

          {destConnections.length === 0 ? (
            <p className="py-2 text-sm text-muted-foreground">
              Connect at least one more cloud storage to transfer files between accounts.
            </p>
          ) : (
            <div className="grid gap-4 py-2">
              <div className="grid gap-2">
                <Label htmlFor="transfer-operation">Operation</Label>
                <select
                  id="transfer-operation"
                  className="h-9 rounded-md border border-input bg-background px-3 text-sm text-foreground"
                  value={mode}
                  onChange={(event) => setMode(event.target.value)}
                >
                  <option value="copy">Copy</option>
                  <option value="move">Move</option>
                </select>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="transfer-destination">Destination storage</Label>
                <select
                  id="transfer-destination"
                  className="h-9 rounded-md border border-input bg-background px-3 text-sm text-foreground"
                  value={destConnectionUuid}
                  onChange={(event) => {
                    setDestConnectionUuid(event.target.value);
                    setDestParentId(ROOT_ID);
                  }}
                >
                  {destConnections.map((connection) => (
                    <option key={connection.uuid} value={connection.uuid}>
                      {connection.display_name || connection.provider_label}
                      {connection.account_email ? ` (${connection.account_email})` : ''}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="transfer-folder">Destination folder</Label>
                <select
                  id="transfer-folder"
                  className="h-9 rounded-md border border-input bg-background px-3 text-sm text-foreground"
                  value={destParentId}
                  onChange={(event) => setDestParentId(event.target.value)}
                  disabled={destFoldersQuery.isLoading}
                >
                  <option value={ROOT_ID}>My Drive (root)</option>
                  {destFolders.map((folder) => (
                    <option
                      key={folder.provider_item_id}
                      value={folder.provider_item_id}
                    >
                      {folder.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="transfer-conflict">If a file already exists</Label>
                <select
                  id="transfer-conflict"
                  className="h-9 rounded-md border border-input bg-background px-3 text-sm text-foreground"
                  value={conflictPolicy}
                  onChange={(event) => setConflictPolicy(event.target.value)}
                >
                  <option value="reject">Stop and report a conflict</option>
                  <option value="rename">Rename the copy</option>
                </select>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={
                destConnections.length === 0 ||
                !destConnectionUuid ||
                createTransfer.isPending
              }
            >
              {createTransfer.isPending ? 'Starting…' : 'Start transfer'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
