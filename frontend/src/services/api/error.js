export class AppError extends Error {
  constructor(message, { status = null, fieldErrors = null, data = null } = {}) {
    super(message);
    this.name = 'AppError';
    this.status = status;
    this.fieldErrors = fieldErrors;
    this.data = data;
  }
}

function firstFieldMessage(fieldErrors) {
  if (!fieldErrors || typeof fieldErrors !== 'object') {
    return null;
  }

  const first = Object.values(fieldErrors)[0];
  if (Array.isArray(first)) {
    return first[0] ?? null;
  }

  return typeof first === 'string' ? first : null;
}

function normalizeFieldErrors(payload) {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    return null;
  }

  const fieldErrors = {};

  for (const [key, value] of Object.entries(payload)) {
    if (key === 'success' || key === 'message' || key === 'data' || key === 'errors' || key === 'detail') {
      continue;
    }

    if (Array.isArray(value)) {
      fieldErrors[key] = value[0] ?? 'Invalid value';
    } else if (typeof value === 'string') {
      fieldErrors[key] = value;
    }
  }

  return Object.keys(fieldErrors).length ? fieldErrors : null;
}

export function normalizeApiError(error) {
  if (error instanceof AppError) {
    return error;
  }

  const status = error?.response?.status ?? null;
  const data = error?.response?.data;

  if (!data) {
    return new AppError(error?.message || 'Network error. Please try again.', {
      status,
    });
  }

  if (typeof data.success === 'boolean') {
    const fieldErrors =
      (data.errors && typeof data.errors === 'object' ? data.errors : null) ||
      normalizeFieldErrors(data);

    return new AppError(data.message || 'Request failed.', {
      status,
      fieldErrors,
      data: data.data ?? null,
    });
  }

  if (data.detail) {
    const message =
      typeof data.detail === 'string'
        ? data.detail
        : Array.isArray(data.detail)
          ? data.detail[0]
          : 'Request failed.';

    return new AppError(message, { status });
  }

  const fieldErrors = normalizeFieldErrors(data);
  const message = firstFieldMessage(fieldErrors) || 'Validation failed.';

  return new AppError(message, { status, fieldErrors });
}
