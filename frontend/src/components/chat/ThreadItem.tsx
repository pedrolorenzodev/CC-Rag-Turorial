import { type Thread } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface ThreadItemProps {
  thread: Thread
  isActive: boolean
  onSelect: () => void
  onDelete: () => void
}

export function ThreadItem({ thread, isActive, onSelect, onDelete }: ThreadItemProps) {
  const title = thread.title || 'New Chat'
  const date = new Date(thread.updated_at).toLocaleDateString()

  return (
    <div
      className={cn(
        'group flex items-center justify-between p-3 rounded-xl cursor-pointer transition-[background-color,transform,box-shadow] duration-200 ease-[cubic-bezier(0.16,1,0.3,1)]',
        isActive
          ? 'bg-gradient-accent shadow-sm border border-border/50'
          : 'hover:bg-accent/60 hover:shadow-sm active:scale-[0.98]'
      )}
      onClick={onSelect}
    >
      <div className="flex-1 min-w-0">
        <p className={cn(
          "text-sm font-medium truncate transition-colors duration-200",
          isActive ? "text-foreground" : "text-foreground/80 group-hover:text-foreground"
        )}>
          {title}
        </p>
        <p className="text-xs text-muted-foreground mt-0.5">{date}</p>
      </div>
      <Button
        variant="ghost"
        size="icon-xs"
        className="opacity-0 group-hover:opacity-100 transition-[opacity,transform] duration-200 hover:bg-destructive/10 hover:text-destructive"
        onClick={(e) => {
          e.stopPropagation()
          onDelete()
        }}
        aria-label="Delete thread"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M3 6h18" />
          <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
          <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
        </svg>
      </Button>
    </div>
  )
}
