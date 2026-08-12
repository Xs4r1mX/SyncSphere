import { unwrapResponse } from '@/services/api/unwrapResponse';

import transferService from '../services/transferService';

export const listTransfers = (params) =>
  unwrapResponse(transferService.listTransfers(params));

export const createTransfer = (payload) =>
  unwrapResponse(transferService.createTransfer(payload));

export const getTransfer = (uuid) =>
  unwrapResponse(transferService.getTransfer(uuid));

export const listTransferItems = (uuid) =>
  unwrapResponse(transferService.listItems(uuid));

export const cancelTransfer = (uuid) =>
  unwrapResponse(transferService.cancelTransfer(uuid));

const transferApi = {
  listTransfers,
  createTransfer,
  getTransfer,
  listTransferItems,
  cancelTransfer,
};

export default transferApi;
