import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';

export function FileBreadcrumb({ items, onNavigate }) {
  if (!items?.length) {
    return null;
  }

  return (
    <Breadcrumb>
      <BreadcrumbList>
        {items.map((item, index) => {
          const isLast = index === items.length - 1;

          return (
            <span key={item.provider_item_id} className="contents">
              {index > 0 ? <BreadcrumbSeparator /> : null}
              <BreadcrumbItem>
                {isLast ? (
                  <BreadcrumbPage>{item.name}</BreadcrumbPage>
                ) : (
                  <BreadcrumbLink
                    onClick={() => onNavigate(item.provider_item_id)}
                  >
                    {item.name}
                  </BreadcrumbLink>
                )}
              </BreadcrumbItem>
            </span>
          );
        })}
      </BreadcrumbList>
    </Breadcrumb>
  );
}
