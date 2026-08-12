import api from '@/services/api/axios';
import endpoints from '@/services/api/endpoints';

const transferService = {
  listTransfers(params = {}) {
    return api.get(endpoints.transfers.list, { params });
  },

  createTransfer(payload) {
    return api.post(endpoints.transfers.list, payload);
  },

  getTransfer(uuid) {
    return api.get(endpoints.transfers.job(uuid));
  },

  listItems(uuid) {
    return api.get(endpoints.transfers.items(uuid));
  },

  cancelTransfer(uuid) {
    return api.post(endpoints.transfers.cancel(uuid));
  },
};

export default transferService;
