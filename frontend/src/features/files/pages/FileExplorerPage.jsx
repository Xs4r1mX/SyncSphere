import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

import { PATHS } from '@/app/routes/paths';
import { PageHeader } from '@/components/layout/PageHeader';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { getMockConnection } from '../data/mockConnections';
import { useMockFileExplorer } from '../hooks/useMockFileExplorer';
import { CopyFileDialog } from '../components/CopyFileDialog';
import { CreateFolderDialog } from '../components/CreateFolderDialog';
import { DeleteFileConfirmDialog } from '../components/DeleteFileConfirmDialog';
import { FileBreadcrumb } from '../components/FileBreadcrumb';
import { FileExplorerToolbar } from '../components/FileExplorerToolbar';
import { FileListTable } from '../components/FileListTable';
import { FileQuotaSummary } from '../components/FileQuotaSummary';
import { RenameFileDialog } from '../components/RenameFileDialog';

export function FileExplorerPage() {
  const { connectionUuid } = useParams();
  const connection = getMockConnection(connectionUuid);

  const {
    items,
    visibleItems,
    breadcrumb,
    isFolderValid,
    showTrashed,
    isLoading,
    setShowTrashed,
    navigateToFolder,
    createFolder,
    renameItem,
    trashItem,
    restoreItem,
    handleUpload,
    handleCopy,
    handleDownload,
    handleMove,
  } = useMockFileExplorer();

  const [createFolderOpen, setCreateFolderOpen] = useState(false);
  const [renameItemState, setRenameItemState] = useState(null);
  const [deleteItemState, setDeleteItemState] = useState(null);
  const [copyItemState, setCopyItemState] = useState(null);

  if (!connection) {
    return (
      <div className="grid gap-6">
        <PageHeader
          title="Files"
          description="The cloud connection could not be found."
        />
        <Alert variant="destructive">
          <AlertDescription>
            This connection link is invalid. Return to cloud storages and try again.
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

  const title = connection.display_name || connection.provider_label;

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

      <FileQuotaSummary connection={connection} />

      <FileExplorerToolbar
        showTrashed={showTrashed}
        onToggleTrashed={setShowTrashed}
        onCreateFolder={() => setCreateFolderOpen(true)}
        onUpload={handleUpload}
      />

      {!showTrashed && breadcrumb ? (
        <FileBreadcrumb items={breadcrumb} onNavigate={navigateToFolder} />
      ) : null}

      {!isFolderValid && !showTrashed ? (
        <Alert variant="destructive">
          <AlertDescription>
            This folder could not be found. It may have been moved or deleted.
          </AlertDescription>
        </Alert>
      ) : null}

      <FileListTable
        items={visibleItems}
        isLoading={isLoading}
        showTrashed={showTrashed}
        onOpenFolder={navigateToFolder}
        onRename={setRenameItemState}
        onDelete={setDeleteItemState}
        onRestore={restoreItem}
        onCopy={setCopyItemState}
        onDownload={handleDownload}
        onMove={handleMove}
      />

      {!isLoading && visibleItems.length > 0 ? (
        <div className="flex justify-center">
          <Button variant="outline" disabled>
            Load more (coming soon)
          </Button>
        </div>
      ) : null}

      <CreateFolderDialog
        open={createFolderOpen}
        onOpenChange={setCreateFolderOpen}
        onSubmit={createFolder}
      />

      <RenameFileDialog
        open={Boolean(renameItemState)}
        onOpenChange={(open) => {
          if (!open) {
            setRenameItemState(null);
          }
        }}
        item={renameItemState}
        onSubmit={renameItem}
      />

      <DeleteFileConfirmDialog
        open={Boolean(deleteItemState)}
        onOpenChange={(open) => {
          if (!open) {
            setDeleteItemState(null);
          }
        }}
        item={deleteItemState}
        onConfirm={trashItem}
      />

      <CopyFileDialog
        open={Boolean(copyItemState)}
        onOpenChange={(open) => {
          if (!open) {
            setCopyItemState(null);
          }
        }}
        item={copyItemState}
        allItems={items}
        onSubmit={handleCopy}
      />
    </div>
  );
}
