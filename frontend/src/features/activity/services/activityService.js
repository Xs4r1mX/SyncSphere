import api from '@/services/api/axios';
import endpoints from '@/services/api/endpoints';

const activityService = {
  listActivity(params = {}) {
    return api.get(endpoints.activity.list, { params });
  },
};

export default activityService;
