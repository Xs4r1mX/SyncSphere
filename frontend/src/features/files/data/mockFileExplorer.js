import { FOLDER_MIME_TYPE, ROOT_ID } from '../constants/fileTypes';

function folder(id, name, parentId) {
  return {
    provider_item_id: id,
    name,
    mime_type: FOLDER_MIME_TYPE,
    is_folder: true,
    parent_id: parentId,
    size: null,
    created_at: '2026-01-10T09:00:00Z',
    modified_at: '2026-03-01T14:30:00Z',
    trashed: false,
    web_view_link: null,
  };
}

function file(id, name, parentId, mimeType, size, modifiedAt = '2026-06-15T10:00:00Z') {
  return {
    provider_item_id: id,
    name,
    mime_type: mimeType,
    is_folder: false,
    parent_id: parentId,
    size,
    created_at: '2026-02-01T08:00:00Z',
    modified_at: modifiedAt,
    trashed: false,
    web_view_link: `https://drive.google.com/file/d/${id}/view`,
  };
}

export const initialMockItems = [
  folder('folder-docs', 'Documents', ROOT_ID),
  folder('folder-photos', 'Photos', ROOT_ID),
  folder('folder-archive', 'Archive', ROOT_ID),
  file('file-readme', 'readme.txt', ROOT_ID, 'text/plain', 2048),
  file('file-presentation', 'Q2 Review.pptx', ROOT_ID, 'application/vnd.openxmlformats-officedocument.presentationml.presentation', 4_194_304),

  file('file-report', 'Annual Report.pdf', 'folder-docs', 'application/pdf', 2_621_440),
  folder('folder-notes', 'Notes', 'folder-docs'),
  file('file-budget', 'Budget.xlsx', 'folder-docs', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 524_288),

  file('file-meeting', 'meeting-notes.docx', 'folder-notes', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 98304),

  file('file-vacation', 'vacation.jpg', 'folder-photos', 'image/jpeg', 3_145_728),
  file('file-family', 'family.png', 'folder-photos', 'image/png', 1_572_864),

  file('file-old-draft', 'old-draft.docx', ROOT_ID, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 45056, '2025-11-20T16:00:00Z'),
];

export function cloneMockItems() {
  return initialMockItems.map((item) => ({ ...item }));
}

export function getFolderOptions(items) {
  return items.filter((item) => item.is_folder && !item.trashed);
}
