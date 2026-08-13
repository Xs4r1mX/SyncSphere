import {
  ArrowLeftRight,
  Cloud,
  CloudOff,
  Copy,
  FilePlus,
  FileText,
  FolderInput,
  FolderPlus,
  Link2,
  Pencil,
  RotateCcw,
  Trash2,
  Unlink,
  Upload,
  XCircle,
} from 'lucide-react';

export const RESOURCE_TYPE_FILTER_OPTIONS = [
  { value: 'all', label: 'All types' },
  { value: 'connection', label: 'Connections' },
  { value: 'file', label: 'Files' },
  { value: 'folder', label: 'Folders' },
  { value: 'transfer', label: 'Transfers' },
];

const ACTION_META = {
  'connection.linked': { label: 'Connection linked', icon: Link2 },
  'connection.unlinked': { label: 'Connection unlinked', icon: Unlink },
  'connection.disabled': { label: 'Connection disabled', icon: CloudOff },
  'connection.enabled': { label: 'Connection enabled', icon: Cloud },
  'file.uploaded': { label: 'File uploaded', icon: Upload },
  'file.folder_created': { label: 'Folder created', icon: FolderPlus },
  'file.renamed': { label: 'Renamed', icon: Pencil },
  'file.moved': { label: 'Moved', icon: FolderInput },
  'file.trashed': { label: 'Moved to trash', icon: Trash2 },
  'file.deleted': { label: 'Deleted permanently', icon: Trash2 },
  'file.copied': { label: 'Copied', icon: Copy },
  'file.restored': { label: 'Restored', icon: RotateCcw },
  'transfer.created': { label: 'Transfer created', icon: ArrowLeftRight },
  'transfer.cancel_requested': { label: 'Transfer cancel requested', icon: XCircle },
  'transfer.cancelled': { label: 'Transfer cancelled', icon: XCircle },
  'transfer.completed': { label: 'Transfer completed', icon: ArrowLeftRight },
  'transfer.failed': { label: 'Transfer failed', icon: XCircle },
};

const RESOURCE_ICONS = {
  connection: Cloud,
  file: FileText,
  folder: FolderPlus,
  transfer: ArrowLeftRight,
};

export function getActivityActionLabel(action) {
  return ACTION_META[action]?.label ?? action?.replaceAll('.', ' ') ?? 'Activity';
}

export function getActivityIcon(action, resourceType) {
  return ACTION_META[action]?.icon ?? RESOURCE_ICONS[resourceType] ?? FilePlus;
}
