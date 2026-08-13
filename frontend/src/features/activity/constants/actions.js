import {
  ArrowLeftRight,
  Cloud,
  CloudOff,
  Copy,
  FilePlus,
  FileText,
  FolderInput,
  FolderPlus,
  KeyRound,
  Link2,
  LogOut,
  MailCheck,
  Pencil,
  RotateCcw,
  Trash2,
  Unlink,
  Upload,
  UserRound,
  XCircle,
} from 'lucide-react';

export const RESOURCE_TYPE_FILTER_OPTIONS = [
  { value: 'all', label: 'All types' },
  { value: 'account', label: 'Account' },
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
  'file.renamed': { label: 'File renamed', icon: Pencil },
  'file.moved': { label: 'File moved', icon: FolderInput },
  'file.trashed': { label: 'File trashed', icon: Trash2 },
  'file.deleted': { label: 'File deleted', icon: Trash2 },
  'file.copied': { label: 'File copied', icon: Copy },
  'file.restored': { label: 'File restored', icon: RotateCcw },
  'transfer.created': { label: 'Transfer created', icon: ArrowLeftRight },
  'transfer.cancel_requested': { label: 'Transfer cancel requested', icon: XCircle },
  'transfer.cancelled': { label: 'Transfer cancelled', icon: XCircle },
  'transfer.completed': { label: 'Transfer completed', icon: ArrowLeftRight },
  'transfer.failed': { label: 'Transfer failed', icon: XCircle },
  'auth.password_changed': { label: 'Password changed', icon: KeyRound },
  'auth.password_reset_requested': { label: 'Password reset requested', icon: KeyRound },
  'auth.password_reset_completed': { label: 'Password reset completed', icon: KeyRound },
  'auth.email_verified': { label: 'Email verified', icon: MailCheck },
  'auth.logout_all_devices': { label: 'Logged out all devices', icon: LogOut },
};

const RESOURCE_ICONS = {
  account: UserRound,
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
