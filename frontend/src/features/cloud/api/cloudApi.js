import { unwrapResponse } from '@/services/api/unwrapResponse';

import cloudService from '../services/cloudService';

export const listConnections = () => unwrapResponse(cloudService.listConnections());

export const getConnection = (uuid) => unwrapResponse(cloudService.getConnection(uuid));

export const authorizeProvider = (provider) =>
  unwrapResponse(cloudService.authorizeProvider(provider));

export const unlinkConnection = (uuid) =>
  unwrapResponse(cloudService.unlinkConnection(uuid));

export const disableConnection = (uuid) =>
  unwrapResponse(cloudService.disableConnection(uuid));

export const getConnectionHealth = (uuid) =>
  unwrapResponse(cloudService.getConnectionHealth(uuid));

const cloudApi = {
  listConnections,
  getConnection,
  authorizeProvider,
  unlinkConnection,
  disableConnection,
  getConnectionHealth,
};

export default cloudApi;
