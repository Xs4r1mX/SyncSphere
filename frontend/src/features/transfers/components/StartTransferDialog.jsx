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
import { SelectField } from '@/components/ui/select';
import { useCloudConnections } from '@/features/cloud/hooks/useCloudConnections';
import { formatConnectionLabel } from '@/features/cloud/utils/formatConnectionLabel';
import { ROOT_ID } from '@/features/files/constants/fileTypes';
import { useFileList } from '@/features/files/hooks/useFileList';
import { useCreateTransfer } from '../hooks/useTransferMutations';

const ROOT_MIGRATE_ITEM = {
  provider_item_id: ROOT_ID,
  name: 'My Drive',
  is_folder: true,
};

export function StartTransferDialog({
  open,
  onOpenChange,
  item,
  sourceConnectionUuid,
  migrateEntire = false,
}) {
  const navigate = useNavigate();
  const connectionsQuery = useCloudConnections();
  const createTransfer = useCreateTransfer();

  const [destConnectionUuid, setDestConnectionUuid] = useState('');
  const [destParentId, setDestParentId] = useState(ROOT_ID);
  const [mode, setMode] = useState('copy');
  const [conflictPolicy, setConflictPolicy] = useState('reject');

  const transferItem = migrateEntire ? ROOT_MIGRATE_ITEM : item;

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

    if (!transferItem || !destConnectionUuid) {
      return;
    }

    const operation =
      transferItem.is_folder || migrateEntire
        ? mode === 'move'
          ? 'move_all'
          : 'copy_all'
        : mode;

    createTransfer.mutate(
      {
        operation,
        source_connection_uuid: sourceConnectionUuid,
        dest_connection_uuid: destConnectionUuid,
        source_item_id: transferItem.provider_item_id,
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

  const title = migrateEntire
    ? 'Migrate entire cloud'
    : 'Transfer to another cloud';

  const description = migrateEntire
    ? 'Copy or move everything from this storage (My Drive) to another connected account.'
    : `Copy or move “${item?.name}” to a different connected storage.`;

  const operationOptions = migrateEntire || transferItem?.is_folder
    ? [
        { value: 'copy', label: 'Copy all' },
        { value: 'move', label: 'Move all' },
      ]
    : [
        { value: 'copy', label: 'Copy' },
        { value: 'move', label: 'Move' },
      ];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>{title}</DialogTitle>
            <DialogDescription>{description}</DialogDescription>
          </DialogHeader>

          {destConnections.length === 0 ? (
            <p className="py-2 text-sm text-muted-foreground">
              Connect at least one more cloud storage to transfer files between accounts.
            </p>
          ) : (
            <div className="grid gap-4 py-2">
              <div className="grid gap-2">
                <Label htmlFor="transfer-operation">Operation</Label>
                <SelectField
                  id="transfer-operation"
                  value={mode}
                  onValueChange={setMode}
                  options={operationOptions}
                />
              </div>

              {mode === 'move' ? (
                <p className="text-sm text-muted-foreground">
                  {migrateEntire
                    ? 'Move all deletes files from the source after they are written to the destination. Root itself is not deleted.'
                    : 'Move deletes the source after a successful write to the destination.'}
                </p>
              ) : null}

              <div className="grid gap-2">
                <Label htmlFor="transfer-destination">Destination storage</Label>
                <SelectField
                  id="transfer-destination"
                  value={destConnectionUuid}
                  onValueChange={(nextUuid) => {
                    setDestConnectionUuid(nextUuid);
                    setDestParentId(ROOT_ID);
                  }}
                  options={destConnections.map((connection) => ({
                    value: connection.uuid,
                    label: formatConnectionLabel(connection),
                  }))}
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="transfer-folder">Destination folder</Label>
                <SelectField
                  id="transfer-folder"
                  value={destParentId}
                  onValueChange={setDestParentId}
                  disabled={destFoldersQuery.isLoading}
                  options={[
                    { value: ROOT_ID, label: 'My Drive (root)' },
                    ...destFolders.map((folder) => ({
                      value: folder.provider_item_id,
                      label: folder.name,
                    })),
                  ]}
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="transfer-conflict">If a file already exists</Label>
                <SelectField
                  id="transfer-conflict"
                  value={conflictPolicy}
                  onValueChange={setConflictPolicy}
                  options={[
                    { value: 'reject', label: 'Stop and report a conflict' },
                    { value: 'rename', label: 'Rename the copy' },
                  ]}
                />
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
