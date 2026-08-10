import api from '@/services/api/axios';
import endpoints from '@/services/api/endpoints';

const fileService = {
  listItems(connectionUuid, params = {}) {
    return api.get(endpoints.files.list(connectionUuid), { params });
  },

  getQuota(connectionUuid) {
    return api.get(endpoints.files.quota(connectionUuid));
  },

  getBreadcrumb(connectionUuid, itemId) {
    return api.get(endpoints.files.breadcrumb(connectionUuid), {
      params: { item_id: itemId },
    });
  },

  createFolder(connectionUuid, payload) {
    return api.post(endpoints.files.folders(connectionUuid), payload);
  },

  uploadFile(connectionUuid, formData) {
    return api.post(endpoints.files.upload(connectionUuid), formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  updateItem(connectionUuid, itemId, payload) {
    return api.patch(endpoints.files.item(connectionUuid, itemId), payload);
  },

  deleteItem(connectionUuid, itemId, params = {}) {
    return api.delete(endpoints.files.item(connectionUuid, itemId), { params });
  },

  downloadFile(connectionUuid, itemId) {
    return api.get(endpoints.files.download(connectionUuid, itemId), {
      responseType: 'blob',
    });
  },

  copyItem(connectionUuid, itemId, payload) {
    return api.post(endpoints.files.copy(connectionUuid, itemId), payload);
  },

  restoreItem(connectionUuid, itemId) {
    return api.post(endpoints.files.restore(connectionUuid, itemId));
  },
};

export default fileService;
