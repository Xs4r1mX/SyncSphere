import { unwrapResponse } from '@/services/api/unwrapResponse';

import activityService from '../services/activityService';

export const listActivity = (params) =>
  unwrapResponse(activityService.listActivity(params));

const activityApi = {
  listActivity,
};

export default activityApi;
