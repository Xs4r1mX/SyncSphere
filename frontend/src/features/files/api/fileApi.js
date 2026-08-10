import { AppError, normalizeApiError } from '@/services/api/error';
import { unwrapResponse } from '@/services/api/unwrapResponse';

import fileService from '../services/fileService';
import { parseFilename } from '../utils/downloadBlob';

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

export async function downloadFile(connectionUuid, itemId) {
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

    return {
      blob: response.data,
      filename: parseFilename(response.headers['content-disposition']),
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
  copyItem,
  restoreItem,
};

export default fileApi;
