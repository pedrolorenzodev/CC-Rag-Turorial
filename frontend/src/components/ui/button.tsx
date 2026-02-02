import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg text-sm font-medium cursor-pointer transition-[transform,background-color,box-shadow,opacity] duration-200 ease-[cubic-bezier(0.16,1,0.3,1)] disabled:pointer-events-none disabled:opacity-50 disabled:cursor-not-allowed [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 [&_svg]:transition-transform [&_svg]:duration-200 outline-none focus-visible:ring-ring/50 focus-visible:ring-[3px] focus-visible:ring-offset-2 focus-visible:ring-offset-background aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive active:scale-[0.98]",
  {
    variants: {
      variant: {
        default: "bg-gradient-primary text-primary-foreground shadow-md shadow-primary/20 hover:shadow-lg hover:shadow-primary/30 hover:brightness-110 active:shadow-sm",
        destructive:
          "bg-destructive text-white shadow-md shadow-destructive/20 hover:bg-destructive/90 hover:shadow-lg hover:shadow-destructive/30 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/80",
        outline:
          "border-2 bg-background/80 backdrop-blur-sm shadow-sm hover:bg-accent hover:text-accent-foreground hover:border-accent-foreground/20 hover:shadow-md dark:bg-input/20 dark:border-input dark:hover:bg-input/40",
        secondary:
          "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80 hover:shadow-md",
        ghost:
          "hover:bg-accent/80 hover:text-accent-foreground dark:hover:bg-accent/50 hover:shadow-sm",
        link: "text-primary underline-offset-4 hover:underline hover:text-primary/80",
      },
      size: {
        default: "h-10 px-5 py-2.5 has-[>svg]:px-4",
        xs: "h-7 gap-1 rounded-md px-2.5 text-xs has-[>svg]:px-2 [&_svg:not([class*='size-'])]:size-3",
        sm: "h-9 rounded-lg gap-1.5 px-4 has-[>svg]:px-3",
        lg: "h-12 rounded-xl px-8 text-base has-[>svg]:px-6",
        icon: "size-10 rounded-xl",
        "icon-xs": "size-7 rounded-lg [&_svg:not([class*='size-'])]:size-3",
        "icon-sm": "size-9 rounded-lg",
        "icon-lg": "size-12 rounded-xl",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant = "default",
  size = "default",
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot : "button"

  return (
    <Comp
      data-slot="button"
      data-variant={variant}
      data-size={size}
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
