import { AppError, normalizeApiError } from '@/services/api/error';
import { unwrapResponse } from '@/services/api/unwrapResponse';

import fileService from '../services/fileService';
import { parseFilename } from '../utils/downloadBlob';
import { resolveViewMimeType } from '../utils/mimeType';

export const listItems = (connectionUuid, params) =>
  unwrapResponse(fileService.listItems(connectionUuid, params));

export const getQuota = (connectionUuid) =>
  unwrapResponse(fileService.getQuota(connectionUuid));

export const getBreadcrumb = (connectionUuid, itemId) =>
  unwrapResponse(fileService.getBreadcrumb(connectionUuid, itemId));

export const createFolder = (connectionUuid, payload) =>
  unwrapResponse(fileService.createFolder(connectionUuid, payload));

export const uploadFile = (connectionUuid, formData) =>
  unwrapResponse(fileService.uploadFile(connectionUuid, formData));

export const updateItem = (connectionUuid, itemId, payload) =>
  unwrapResponse(fileService.updateItem(connectionUuid, itemId, payload));

export const deleteItem = (connectionUuid, itemId, params) =>
  unwrapResponse(fileService.deleteItem(connectionUuid, itemId, params));

export const copyItem = (connectionUuid, itemId, payload) =>
  unwrapResponse(fileService.copyItem(connectionUuid, itemId, payload));

export const restoreItem = (connectionUuid, itemId) =>
  unwrapResponse(fileService.restoreItem(connectionUuid, itemId));

export async function openFile(connectionUuid, item) {
  if (item.web_view_link) {
    return { mode: 'direct', url: item.web_view_link };
  }

  try {
    const { open_url: openUrl } = await unwrapResponse(
      fileService.openFile(connectionUuid, item.provider_item_id),
    );
    if (openUrl) {
      return { mode: 'direct', url: openUrl };
    }
  } catch {
    // Fall back to inline blob preview when provider preview links are unavailable.
  }

  const { blob, filename } = await downloadFile(
    connectionUuid,
    item.provider_item_id,
    item.name,
  );
  const mimeType = resolveViewMimeType(item.mime_type, filename, blob.type);
  const viewBlob =
    blob.type === mimeType ? blob : new Blob([blob], { type: mimeType });

  return {
    mode: 'blob',
    url: URL.createObjectURL(viewBlob),
  };
}

export async function downloadFile(connectionUuid, itemId, fallbackFilename) {
  try {
    const response = await fileService.downloadFile(connectionUuid, itemId);
    const contentType = response.headers['content-type'] ?? '';

    if (contentType.includes('application/json')) {
      const text = await response.data.text();
      const body = JSON.parse(text);
      throw new AppError(body.message || 'Download failed.', {
        status: response.status,
      });
    }

    const parsedFilename = parseFilename(response.headers['content-disposition']);
    const filename =
      parsedFilename !== 'download' ? parsedFilename : fallbackFilename || 'download';

    return {
      blob: response.data,
      filename,
    };
  } catch (error) {
    if (error instanceof AppError) {
      throw error;
    }

    if (error?.response?.data instanceof Blob) {
      const contentType = error.response.headers['content-type'] ?? '';

      if (contentType.includes('application/json')) {
        const text = await error.response.data.text();
        const body = JSON.parse(text);
        throw new AppError(body.message || 'Download failed.', {
          status: error.response.status,
        });
      }
    }

    throw normalizeApiError(error);
  }
}

const fileApi = {
  listItems,
  getQuota,
  getBreadcrumb,
  createFolder,
  uploadFile,
  updateItem,
  deleteItem,
  downloadFile,
  openFile,
  copyItem,
  restoreItem,
};

export default fileApi;
