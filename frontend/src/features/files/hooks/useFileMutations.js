import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import fileApi from '../api/fileApi';
import { triggerBlobDownload } from '../utils/downloadBlob';
import { fileQueryKeys } from '../constants/queryKeys';

function invalidateFileQueries(queryClient, connectionUuid) {
  queryClient.invalidateQueries({ queryKey: fileQueryKeys.all });
  queryClient.invalidateQueries({
    queryKey: ['cloud', 'connection', connectionUuid],
  });
}

export function useCreateFolder(connectionUuid) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ name, parentId }) =>
      fileApi.createFolder(connectionUuid, {
        name,
        parent_id: parentId,
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: fileQueryKeys.list(connectionUuid, variables.parentId, false),
      });
      toast.success('Folder created.');
    },
    onError: (error) => {
      toast.error(error.message || 'Could not create folder.');
    },
  });
}

export function useUploadFile(connectionUuid) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, name, parentId }) => {
      const formData = new FormData();
      formData.append('file', file);

      if (name) {
        formData.append('name', name);
      }

      formData.append('parent_id', parentId);
      return fileApi.uploadFile(connectionUuid, formData);
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: fileQueryKeys.list(connectionUuid, variables.parentId, false),
      });
      queryClient.invalidateQueries({
        queryKey: fileQueryKeys.quota(connectionUuid),
      });
      toast.success('File uploaded.');
    },
    onError: (error) => {
      toast.error(error.message || 'Could not upload file.');
    },
  });
}

export function useUpdateFile(connectionUuid) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ itemId, name, parentId }) =>
      fileApi.updateItem(connectionUuid, itemId, {
        ...(name !== undefined ? { name } : {}),
        ...(parentId !== undefined ? { parent_id: parentId } : {}),
      }),
    onSuccess: () => {
      invalidateFileQueries(queryClient, connectionUuid);
      toast.success('Item updated.');
    },
    onError: (error) => {
      toast.error(error.message || 'Could not update item.');
    },
  });
}

export function useDeleteFile(connectionUuid) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ itemId, permanent = false }) =>
      fileApi.deleteItem(connectionUuid, itemId, { permanent }),
    onSuccess: () => {
      invalidateFileQueries(queryClient, connectionUuid);
      toast.success('Moved to trash.');
    },
    onError: (error) => {
      toast.error(error.message || 'Could not delete item.');
    },
  });
}

export function useCopyFile(connectionUuid) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ itemId, parentId, name }) =>
      fileApi.copyItem(connectionUuid, itemId, {
        parent_id: parentId,
        ...(name ? { name } : {}),
      }),
    onSuccess: () => {
      invalidateFileQueries(queryClient, connectionUuid);
      toast.success('Item copied.');
    },
    onError: (error) => {
      toast.error(error.message || 'Could not copy item.');
    },
  });
}

export function useRestoreFile(connectionUuid) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (itemId) => fileApi.restoreItem(connectionUuid, itemId),
    onSuccess: () => {
      invalidateFileQueries(queryClient, connectionUuid);
      toast.success('Item restored.');
    },
    onError: (error) => {
      toast.error(error.message || 'Could not restore item.');
    },
  });
}

export function useDownloadFile(connectionUuid) {
  return useMutation({
    mutationFn: (itemId) => fileApi.downloadFile(connectionUuid, itemId),
    onSuccess: ({ blob, filename }) => {
      triggerBlobDownload(blob, filename);
      toast.success('Download started.');
    },
    onError: (error) => {
      toast.error(error.message || 'Could not download file.');
    },
  });
}
