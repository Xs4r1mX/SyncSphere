const EXTENSION_MIME_TYPES = {
  png: 'image/png',
  jpg: 'image/jpeg',
  jpeg: 'image/jpeg',
  gif: 'image/gif',
  webp: 'image/webp',
  svg: 'image/svg+xml',
  pdf: 'application/pdf',
  txt: 'text/plain',
  html: 'text/html',
  json: 'application/json',
};

export function guessMimeType(filename, fallback = 'application/octet-stream') {
  const extension = filename?.split('.').pop()?.toLowerCase();
  if (!extension) {
    return fallback;
  }
  return EXTENSION_MIME_TYPES[extension] ?? fallback;
}

export function resolveViewMimeType(itemMimeType, filename, blobType) {
  if (itemMimeType && itemMimeType !== 'application/octet-stream') {
    return itemMimeType;
  }
  if (blobType && blobType !== 'application/octet-stream') {
    return blobType;
  }
  return guessMimeType(filename);
}
