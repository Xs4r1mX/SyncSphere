import {
  File,
  FileArchive,
  FileImage,
  FileSpreadsheet,
  FileText,
  FileVideo,
  Folder,
  Presentation,
} from 'lucide-react';

export function getFileIcon(item) {
  if (item.is_folder) {
    return Folder;
  }

  const mimeType = item.mime_type ?? '';

  if (mimeType.startsWith('image/')) {
    return FileImage;
  }

  if (mimeType.startsWith('video/')) {
    return FileVideo;
  }

  if (mimeType.includes('spreadsheet') || mimeType.includes('excel')) {
    return FileSpreadsheet;
  }

  if (mimeType.includes('presentation') || mimeType.includes('powerpoint')) {
    return Presentation;
  }

  if (mimeType.startsWith('text/') || mimeType.includes('pdf') || mimeType.includes('word')) {
    return FileText;
  }

  if (mimeType.includes('zip') || mimeType.includes('archive')) {
    return FileArchive;
  }

  return File;
}
