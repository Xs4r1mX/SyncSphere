import { unwrapResponse } from '@/services/api/unwrapResponse';

import activityService from '../services/activityService';

export const listActivity = (params) =>
  unwrapResponse(activityService.listActivity(params));

export const getActivity = (uuid) =>
  unwrapResponse(activityService.getActivity(uuid));

const activityApi = {
  listActivity,
  getActivity,
};

export default activityApi;
