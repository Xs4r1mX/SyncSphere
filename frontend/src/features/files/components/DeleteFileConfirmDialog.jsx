import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

export function DeleteFileConfirmDialog({
  open,
  onOpenChange,
  item,
  permanent = false,
  onConfirm,
}) {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>
            {permanent ? 'Delete permanently?' : 'Move to trash?'}
          </AlertDialogTitle>
          <AlertDialogDescription>
            {permanent
              ? `“${item?.name}” will be permanently deleted and cannot be restored.`
              : `“${item?.name}” will be moved to trash. You can restore it later from the trash view.`}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction
            variant="destructive"
            onClick={() => {
              if (item) {
                onConfirm(item.provider_item_id);
              }
              onOpenChange(false);
            }}
          >
            {permanent ? 'Delete permanently' : 'Move to trash'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
