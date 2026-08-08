import { useCallback, useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { toast } from 'sonner';

import { FOLDER_MIME_TYPE, ROOT_ID } from '../constants/fileTypes';
import { cloneMockItems } from '../data/mockFileExplorer';

const LOADING_DELAY_MS = 350;

function buildBreadcrumb(items, folderId) {
  if (folderId === ROOT_ID) {
    return [{ provider_item_id: ROOT_ID, name: 'My Drive', is_folder: true }];
  }

  const trail = [];
  let currentId = folderId;

  while (currentId && currentId !== ROOT_ID) {
    const folder = items.find(
      (item) => item.provider_item_id === currentId && item.is_folder,
    );

    if (!folder) {
      return null;
    }

    trail.unshift(folder);
    currentId = folder.parent_id;
  }

  return [{ provider_item_id: ROOT_ID, name: 'My Drive', is_folder: true }, ...trail];
}

function folderExists(items, folderId) {
  if (folderId === ROOT_ID) {
    return true;
  }

  return items.some(
    (item) => item.provider_item_id === folderId && item.is_folder && !item.trashed,
  );
}

export function useMockFileExplorer() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [items, setItems] = useState(() => cloneMockItems());
  const [showTrashed, setShowTrashed] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const folderId = searchParams.get('folder') ?? ROOT_ID;

  useEffect(() => {
    setIsLoading(true);
    const timer = window.setTimeout(() => setIsLoading(false), LOADING_DELAY_MS);
    return () => window.clearTimeout(timer);
  }, [folderId, showTrashed]);

  const breadcrumb = useMemo(
    () => buildBreadcrumb(items, folderId),
    [items, folderId],
  );

  const isFolderValid = folderExists(items, folderId);

  const visibleItems = useMemo(() => {
    if (!isFolderValid) {
      return [];
    }

    return items
      .filter((item) => item.parent_id === folderId && item.trashed === showTrashed)
      .sort((a, b) => {
        if (a.is_folder !== b.is_folder) {
          return a.is_folder ? -1 : 1;
        }

        return a.name.localeCompare(b.name);
      });
  }, [items, folderId, showTrashed, isFolderValid]);

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
    (name) => {
      const trimmedName = name.trim();

      if (!trimmedName) {
        return false;
      }

      const duplicate = items.some(
        (item) =>
          item.parent_id === folderId &&
          !item.trashed &&
          item.name.toLowerCase() === trimmedName.toLowerCase(),
      );

      if (duplicate) {
        toast.error('A file or folder with this name already exists.');
        return false;
      }

      const newFolder = {
        provider_item_id: `folder-${crypto.randomUUID()}`,
        name: trimmedName,
        mime_type: FOLDER_MIME_TYPE,
        is_folder: true,
        parent_id: folderId,
        size: null,
        created_at: new Date().toISOString(),
        modified_at: new Date().toISOString(),
        trashed: false,
        web_view_link: null,
      };

      setItems((current) => [...current, newFolder]);
      toast.success('Folder created.');
      return true;
    },
    [folderId, items],
  );

  const renameItem = useCallback(
    (itemId, name) => {
      const trimmedName = name.trim();

      if (!trimmedName) {
        return false;
      }

      const target = items.find((item) => item.provider_item_id === itemId);

      if (!target) {
        return false;
      }

      const duplicate = items.some(
        (item) =>
          item.provider_item_id !== itemId &&
          item.parent_id === target.parent_id &&
          !item.trashed &&
          item.name.toLowerCase() === trimmedName.toLowerCase(),
      );

      if (duplicate) {
        toast.error('A file or folder with this name already exists.');
        return false;
      }

      setItems((current) =>
        current.map((item) =>
          item.provider_item_id === itemId
            ? { ...item, name: trimmedName, modified_at: new Date().toISOString() }
            : item,
        ),
      );
      toast.success('Item renamed.');
      return true;
    },
    [items],
  );

  const trashItem = useCallback((itemId) => {
    setItems((current) =>
      current.map((item) =>
        item.provider_item_id === itemId
          ? { ...item, trashed: true, modified_at: new Date().toISOString() }
          : item,
      ),
    );
    toast.success('Moved to trash.');
  }, []);

  const restoreItem = useCallback((itemId) => {
    setItems((current) =>
      current.map((item) =>
        item.provider_item_id === itemId
          ? { ...item, trashed: false, modified_at: new Date().toISOString() }
          : item,
      ),
    );
    toast.success('Item restored.');
  }, []);

  const handleUpload = useCallback(() => {
    toast.info('File upload will be available once API integration is complete.');
  }, []);

  const handleCopy = useCallback(() => {
    toast.info('Copy will be available once API integration is complete.');
  }, []);

  const handleDownload = useCallback(() => {
    toast.info('Download will be available once API integration is complete.');
  }, []);

  const handleMove = useCallback(() => {
    toast.info('Move will be available once API integration is complete.');
  }, []);

  return {
    folderId,
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
  };
}
