import type { HTMLAttributes, ReactNode } from "react";
import { classNames } from "../../services/utils";

export function Card({ className, children, ...rest }: HTMLAttributes<HTMLDivElement> & { children: ReactNode }) {
  return (
    <div className={classNames("rounded-lg border border-slate-200 bg-white", className)} {...rest}>
      {children}
    </div>
  );
}

export function CardHeader({ className, children, ...rest }: HTMLAttributes<HTMLDivElement> & { children: ReactNode }) {
  return (
    <div className={classNames("px-5 py-4 border-b border-slate-200", className)} {...rest}>
      {children}
    </div>
  );
}

export function CardBody({ className, children, ...rest }: HTMLAttributes<HTMLDivElement> & { children: ReactNode }) {
  return (
    <div className={classNames("px-5 py-4", className)} {...rest}>
      {children}
    </div>
  );
}

export function CardFooter({ className, children, ...rest }: HTMLAttributes<HTMLDivElement> & { children: ReactNode }) {
  return (
    <div className={classNames("px-5 py-3 border-t border-slate-200 bg-slate-50 rounded-b-lg", className)} {...rest}>
      {children}
    </div>
  );
}
