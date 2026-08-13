import api from '@/services/api/axios';
import endpoints from '@/services/api/endpoints';

const activityService = {
  listActivity(params = {}) {
    return api.get(endpoints.activity.list, { params });
  },

  getActivity(uuid) {
    return api.get(endpoints.activity.detail(uuid));
  },
};

export default activityService;
