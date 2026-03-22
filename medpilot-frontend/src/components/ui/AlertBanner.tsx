import { cn } from "@/lib/utils/cn";

type Variant = "warning" | "danger" | "info" | "success";

interface AlertBannerProps {
  variant: Variant;
  title: string;
  children?: React.ReactNode;
  className?: string;
}

const styles: Record<Variant, { wrap: string; title: string }> = {
  warning: { wrap: "bg-amber-50 border-amber-200 dark:bg-amber-900/20 dark:border-amber-800", title: "text-amber-800 dark:text-amber-300" },
  danger:  { wrap: "bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800",         title: "text-red-800 dark:text-red-300" },
  info:    { wrap: "bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800",     title: "text-blue-800 dark:text-blue-300" },
  success: { wrap: "bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800", title: "text-green-800 dark:text-green-300" },
};

export function AlertBanner({ variant, title, children, className }: AlertBannerProps) {
  return (
    <div className={cn("border rounded-lg px-4 py-3", styles[variant].wrap, className)}>
      <p className={cn("text-sm font-medium", styles[variant].title)}>{title}</p>
      {children && <div className="mt-1 text-xs text-gray-600 dark:text-gray-400">{children}</div>}
    </div>
  );
}
