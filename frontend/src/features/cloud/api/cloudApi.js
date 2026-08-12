import { unwrapResponse } from '@/services/api/unwrapResponse';

import cloudService from '../services/cloudService';

export const listConnections = () => unwrapResponse(cloudService.listConnections());

export const getConnection = (uuid) => unwrapResponse(cloudService.getConnection(uuid));

export const updateConnection = (uuid, payload) =>
  unwrapResponse(cloudService.updateConnection(uuid, payload));

export const authorizeProvider = (provider) =>
  unwrapResponse(cloudService.authorizeProvider(provider));

export const unlinkConnection = (uuid) =>
  unwrapResponse(cloudService.unlinkConnection(uuid));

export const disableConnection = (uuid) =>
  unwrapResponse(cloudService.disableConnection(uuid));

export const enableConnection = (uuid) =>
  unwrapResponse(cloudService.enableConnection(uuid));

export const getConnectionHealth = (uuid) =>
  unwrapResponse(cloudService.getConnectionHealth(uuid));

const cloudApi = {
  listConnections,
  getConnection,
  updateConnection,
  authorizeProvider,
  unlinkConnection,
  disableConnection,
  enableConnection,
  getConnectionHealth,
};

export default cloudApi;
