import api from '@/services/api/axios';
import endpoints from '@/services/api/endpoints';

const cloudService = {
  listConnections() {
    return api.get(endpoints.cloud.connections);
  },

  getConnection(uuid) {
    return api.get(endpoints.cloud.connection(uuid));
  },

  updateConnection(uuid, payload) {
    return api.patch(endpoints.cloud.connection(uuid), payload);
  },

  authorizeProvider(provider) {
    return api.get(endpoints.cloud.providerAuthorize(provider));
  },

  unlinkConnection(uuid) {
    return api.post(endpoints.cloud.connectionUnlink(uuid));
  },

  disableConnection(uuid) {
    return api.post(endpoints.cloud.connectionDisable(uuid));
  },

  enableConnection(uuid) {
    return api.post(endpoints.cloud.connectionEnable(uuid));
  },

  getConnectionHealth(uuid) {
    return api.get(endpoints.cloud.connectionHealth(uuid));
  },
};

export default cloudService;
