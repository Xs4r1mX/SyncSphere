import { AppError, normalizeApiError } from '@/services/api/error';

export async function unwrapResponse(request) {
  try {
    const response = await request;
    const body = response.data;

    if (body && typeof body.success === 'boolean' && body.success === false) {
      throw new AppError(body.message || 'Request failed.', {
        status: response.status,
        fieldErrors: body.errors,
        data: body.data,
      });
    }

    if (body && typeof body.success === 'boolean') {
      return body.data;
    }

    return body;
  } catch (error) {
    throw normalizeApiError(error);
  }
}
