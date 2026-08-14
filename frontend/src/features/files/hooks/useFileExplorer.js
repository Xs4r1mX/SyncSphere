import { useCallback, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

import { getRootBreadcrumbItem } from '@/features/cloud/utils/getProviderRootLabel';
import { ROOT_ID } from '../constants/fileTypes';
import { MAX_UPLOAD_BYTES } from '../constants/fileTypes';
import { buildFolderOptions } from '../utils/buildFolderOptions';
import { useFileBreadcrumb } from './useFileBreadcrumb';
import { useFileList } from './useFileList';
import {
  useCopyFile,
  useCreateFolder,
  useDeleteFile,
  useDownloadFile,
  useRestoreFile,
  useUpdateFile,
  useUploadFile,
} from './useFileMutations';

export function useFileExplorer(connectionUuid, provider = 'google_drive') {
  const rootBreadcrumb = useMemo(
    () => [getRootBreadcrumbItem(provider)],
    [provider],
  );
  const [searchParams, setSearchParams] = useSearchParams();
  const [showTrashed, setShowTrashed] = useState(false);

  const folderId = searchParams.get('folder') ?? ROOT_ID;

  const fileListQuery = useFileList(connectionUuid, {
    parentId: folderId,
    trashed: showTrashed,
  });

  const breadcrumbQuery = useFileBreadcrumb(
    connectionUuid,
    folderId,
    !showTrashed,
  );

  const createFolderMutation = useCreateFolder(connectionUuid);
  const uploadFileMutation = useUploadFile(connectionUuid);
  const updateFileMutation = useUpdateFile(connectionUuid);
  const deleteFileMutation = useDeleteFile(connectionUuid);
  const copyFileMutation = useCopyFile(connectionUuid);
  const restoreFileMutation = useRestoreFile(connectionUuid);
  const downloadFileMutation = useDownloadFile(connectionUuid);

  const visibleItems = useMemo(
    () => fileListQuery.data?.pages.flatMap((page) => page.items) ?? [],
    [fileListQuery.data],
  );

  const breadcrumb = useMemo(() => {
    if (showTrashed) {
      return null;
    }

    if (folderId === ROOT_ID) {
      return rootBreadcrumb;
    }

    if (breadcrumbQuery.data?.length) {
      return breadcrumbQuery.data;
    }

    return rootBreadcrumb;
  }, [showTrashed, folderId, breadcrumbQuery.data, rootBreadcrumb]);

  const folderOptions = useMemo(
    () =>
      buildFolderOptions(
        breadcrumbQuery.data ?? rootBreadcrumb,
        visibleItems,
        null,
        provider,
      ),
    [breadcrumbQuery.data, visibleItems, rootBreadcrumb, provider],
  );

  const navigateToFolder = useCallback(
    (nextFolderId) => {
      if (nextFolderId === ROOT_ID) {
        setSearchParams({});
        return;
      }

      setSearchParams({ folder: nextFolderId });
    },
    [setSearchParams],
  );

  const createFolder = useCallback(
    async (name) => {
      const trimmedName = name.trim();

      if (!trimmedName) {
        return false;
      }

      try {
        await createFolderMutation.mutateAsync({
          name: trimmedName,
          parentId: folderId,
        });
        return true;
      } catch {
        return false;
      }
    },
    [createFolderMutation, folderId],
  );

  const renameItem = useCallback(
    async (itemId, name) => {
      const trimmedName = name.trim();

      if (!trimmedName) {
        return false;
      }

      try {
        await updateFileMutation.mutateAsync({
          itemId,
          name: trimmedName,
        });
        return true;
      } catch {
        return false;
      }
    },
    [updateFileMutation],
  );

  const trashItem = useCallback(
    (itemId) => {
      deleteFileMutation.mutate({ itemId });
    },
    [deleteFileMutation],
  );

  const restoreItem = useCallback(
    (itemId) => {
      restoreFileMutation.mutate(itemId);
    },
    [restoreFileMutation],
  );

  const handleUpload = useCallback(
    (file) => {
      if (!file) {
        return;
      }

      if (file.size > MAX_UPLOAD_BYTES) {
        toast.error('File exceeds the maximum upload size of 100 MB.');
        return;
      }

      uploadFileMutation.mutate({
        file,
        name: file.name,
        parentId: folderId,
      });
    },
    [uploadFileMutation, folderId],
  );

  const handleCopy = useCallback(
    async (itemId, { name, parentId }) => {
      try {
        await copyFileMutation.mutateAsync({
          itemId,
          name: name.trim(),
          parentId,
        });
        return true;
      } catch {
        return false;
      }
    },
    [copyFileMutation],
  );

  const handleMove = useCallback(
    async (itemId, parentId) => {
      try {
        await updateFileMutation.mutateAsync({
          itemId,
          parentId,
        });
        return true;
      } catch {
        return false;
      }
    },
    [updateFileMutation],
  );

  const handleDownload = useCallback(
    (item) => {
      if (item?.is_folder) {
        return;
      }

      downloadFileMutation.mutate({
        itemId: item.provider_item_id,
        filename: item.name,
      });
    },
    [downloadFileMutation],
  );

  const isFolderValid =
    folderId === ROOT_ID ||
    !fileListQuery.isError ||
    fileListQuery.error?.status !== 404;

  return {
    folderId,
    visibleItems,
    breadcrumb,
    folderOptions,
    showTrashed,
    isLoading: fileListQuery.isLoading,
    isFetching: fileListQuery.isFetching,
    isError: fileListQuery.isError,
    error: fileListQuery.error,
    isFolderValid,
    hasNextPage: fileListQuery.hasNextPage,
    isFetchingNextPage: fileListQuery.isFetchingNextPage,
    fetchNextPage: fileListQuery.fetchNextPage,
    setShowTrashed,
    navigateToFolder,
    createFolder,
    renameItem,
    trashItem,
    restoreItem,
    handleUpload,
    handleCopy,
    handleMove,
    handleDownload,
    isUploading: uploadFileMutation.isPending,
  };
}
