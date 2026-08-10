import { useState } from 'react';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { toast } from 'sonner';

import { PATHS } from '@/app/routes/paths';
import { PageHeader } from '@/components/layout/PageHeader';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import cloudApi from '@/features/cloud/api/cloudApi';
import { cloudQueryKeys } from '@/features/cloud/constants/queryKeys';
import { CopyFileDialog } from '../components/CopyFileDialog';
import { CreateFolderDialog } from '../components/CreateFolderDialog';
import { DeleteFileConfirmDialog } from '../components/DeleteFileConfirmDialog';
import { FileBreadcrumb } from '../components/FileBreadcrumb';
import { FileExplorerToolbar } from '../components/FileExplorerToolbar';
import { FileListTable } from '../components/FileListTable';
import { FileQuotaSummary } from '../components/FileQuotaSummary';
import { MoveFileDialog } from '../components/MoveFileDialog';
import { RenameFileDialog } from '../components/RenameFileDialog';
import { MAX_UPLOAD_BYTES, ROOT_ID } from '../constants/fileTypes';
import { useFileBreadcrumb } from '../hooks/useFileBreadcrumb';
import { useFileList } from '../hooks/useFileList';
import { useFileQuota } from '../hooks/useFileQuota';
import {
  useCopyFile,
  useCreateFolder,
  useDeleteFile,
  useDownloadFile,
  useRestoreFile,
  useUpdateFile,
  useUploadFile,
} from '../hooks/useFileMutations';
import { buildFolderOptions } from '../utils/buildFolderOptions';
import { formatFileSize } from '../utils/formatFileSize';

const ROOT_BREADCRUMB = [
  { provider_item_id: ROOT_ID, name: 'My Drive', is_folder: true },
];

export function FileExplorerPage() {
  const { connectionUuid } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const [showTrashed, setShowTrashed] = useState(false);

  const folderId = searchParams.get('folder') ?? ROOT_ID;

  const [createFolderOpen, setCreateFolderOpen] = useState(false);
  const [renameItemState, setRenameItemState] = useState(null);
  const [deleteItemState, setDeleteItemState] = useState(null);
  const [copyItemState, setCopyItemState] = useState(null);
  const [moveItemState, setMoveItemState] = useState(null);

  const connectionQuery = useQuery({
    queryKey: cloudQueryKeys.connection(connectionUuid),
    queryFn: () => cloudApi.getConnection(connectionUuid),
    enabled: Boolean(connectionUuid),
    retry: false,
  });

  const fileListQuery = useFileList(connectionUuid, {
    parentId: folderId,
    trashed: showTrashed,
  });

  const breadcrumbQuery = useFileBreadcrumb(
    connectionUuid,
    folderId,
    !showTrashed,
  );

  const quotaQuery = useFileQuota(connectionUuid);

  const createFolder = useCreateFolder(connectionUuid);
  const uploadFile = useUploadFile(connectionUuid);
  const updateFile = useUpdateFile(connectionUuid);
  const deleteFile = useDeleteFile(connectionUuid);
  const copyFile = useCopyFile(connectionUuid);
  const restoreFile = useRestoreFile(connectionUuid);
  const downloadFile = useDownloadFile(connectionUuid);

  const visibleItems =
    fileListQuery.data?.pages.flatMap((page) => page.items) ?? [];

  const breadcrumb =
    folderId === ROOT_ID
      ? ROOT_BREADCRUMB
      : breadcrumbQuery.data ?? null;

  const folderOptions = buildFolderOptions(
    breadcrumb,
    visibleItems,
    copyItemState?.provider_item_id ?? moveItemState?.provider_item_id,
  );

  const navigateToFolder = (nextFolderId) => {
    if (nextFolderId === ROOT_ID) {
      setSearchParams({});
      return;
    }

    setSearchParams({ folder: nextFolderId });
  };

  const handleUpload = (file) => {
    if (file.size > MAX_UPLOAD_BYTES) {
      toast.error(
        `File exceeds the maximum upload size of ${formatFileSize(MAX_UPLOAD_BYTES)}.`,
      );
      return;
    }

    uploadFile.mutate({
      file,
      parentId: folderId,
    });
  };

  if (connectionQuery.isLoading) {
    return (
      <div className="grid gap-6">
        <PageHeader title="Files" description="Loading cloud connection…" />
      </div>
    );
  }

  if (connectionQuery.isError || !connectionQuery.data) {
    return (
      <div className="grid gap-6">
        <PageHeader
          title="Files"
          description="The cloud connection could not be found."
        />
        <Alert variant="destructive">
          <AlertDescription>
            {connectionQuery.error?.message ||
              'This connection link is invalid. Return to cloud storages and try again.'}
          </AlertDescription>
        </Alert>
        <div>
          <Button render={<Link to={PATHS.CLOUD_STORAGES} />}>
            <ArrowLeft />
            Back to connections
          </Button>
        </div>
      </div>
    );
  }

  const connection = connectionQuery.data;
  const title = connection.display_name || connection.provider_label;
  const quotaUsed =
    quotaQuery.data?.quota_used_bytes ?? connection.quota_used_bytes;
  const quotaTotal =
    quotaQuery.data?.quota_total_bytes ?? connection.quota_total_bytes;

  return (
    <div className="grid gap-6">
      <PageHeader
        title={`${title} — Files`}
        description={
          connection.account_email
            ? `Browsing files for ${connection.account_email}.`
            : 'Browse and manage files in this cloud storage.'
        }
        action={
          <Button render={<Link to={PATHS.CLOUD_STORAGES} />} variant="outline">
            <ArrowLeft />
            Back to connections
          </Button>
        }
      />

      <FileQuotaSummary
        quotaUsedBytes={quotaUsed}
        quotaTotalBytes={quotaTotal}
        isLoading={quotaQuery.isLoading}
      />

      <FileExplorerToolbar
        showTrashed={showTrashed}
        isUploading={uploadFile.isPending}
        onToggleTrashed={setShowTrashed}
        onCreateFolder={() => setCreateFolderOpen(true)}
        onUpload={handleUpload}
      />

      {!showTrashed && breadcrumb ? (
        <FileBreadcrumb items={breadcrumb} onNavigate={navigateToFolder} />
      ) : null}

      {fileListQuery.isError ? (
        <Alert variant="destructive">
          <AlertDescription>
            {fileListQuery.error.message || 'Could not load files.'}
          </AlertDescription>
        </Alert>
      ) : null}

      <FileListTable
        items={visibleItems}
        isLoading={fileListQuery.isLoading}
        showTrashed={showTrashed}
        onOpenFolder={navigateToFolder}
        onRename={setRenameItemState}
        onDelete={setDeleteItemState}
        onRestore={(itemId) => restoreFile.mutate(itemId)}
        onCopy={setCopyItemState}
        onDownload={(item) => downloadFile.mutate(item.provider_item_id)}
        onMove={setMoveItemState}
      />

      {fileListQuery.hasNextPage ? (
        <div className="flex justify-center">
          <Button
            variant="outline"
            disabled={fileListQuery.isFetchingNextPage}
            onClick={() => fileListQuery.fetchNextPage()}
          >
            {fileListQuery.isFetchingNextPage ? 'Loading…' : 'Load more'}
          </Button>
        </div>
      ) : null}

      <CreateFolderDialog
        open={createFolderOpen}
        onOpenChange={setCreateFolderOpen}
        isSubmitting={createFolder.isPending}
        onSubmit={(name) => {
          createFolder.mutate(
            { name, parentId: folderId },
            { onSuccess: () => setCreateFolderOpen(false) },
          );
        }}
      />

      <RenameFileDialog
        open={Boolean(renameItemState)}
        onOpenChange={(open) => {
          if (!open) {
            setRenameItemState(null);
          }
        }}
        item={renameItemState}
        isSubmitting={updateFile.isPending}
        onSubmit={(itemId, name) => {
          updateFile.mutate(
            { itemId, name },
            { onSuccess: () => setRenameItemState(null) },
          );
        }}
      />

      <DeleteFileConfirmDialog
        open={Boolean(deleteItemState)}
        onOpenChange={(open) => {
          if (!open) {
            setDeleteItemState(null);
          }
        }}
        item={deleteItemState}
        onConfirm={(itemId) => {
          deleteFile.mutate({ itemId });
        }}
      />

      <CopyFileDialog
        open={Boolean(copyItemState)}
        onOpenChange={(open) => {
          if (!open) {
            setCopyItemState(null);
          }
        }}
        item={copyItemState}
        folderOptions={folderOptions}
        isSubmitting={copyFile.isPending}
        onSubmit={({ name, parentId }) => {
          if (!copyItemState) {
            return;
          }

          copyFile.mutate(
            {
              itemId: copyItemState.provider_item_id,
              parentId,
              name,
            },
            {
              onSuccess: () => setCopyItemState(null),
            },
          );
        }}
      />

      <MoveFileDialog
        open={Boolean(moveItemState)}
        onOpenChange={(open) => {
          if (!open) {
            setMoveItemState(null);
          }
        }}
        item={moveItemState}
        folderOptions={folderOptions}
        isSubmitting={updateFile.isPending}
        onSubmit={({ parentId }) => {
          if (!moveItemState) {
            return;
          }

          updateFile.mutate(
            {
              itemId: moveItemState.provider_item_id,
              parentId,
            },
            {
              onSuccess: () => setMoveItemState(null),
            },
          );
        }}
      />
    </div>
  );
}
