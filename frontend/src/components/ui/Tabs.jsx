import { createContext, useContext, useMemo } from 'react'
import { clsx } from 'clsx'

const TabsContext = createContext(null)

function useTabsContext(component) {
  const context = useContext(TabsContext)
  if (!context) {
    throw new Error(`${component} must be used within <Tabs> component`)
  }
  return context
}

export function Tabs({ value, onValueChange, className, children }) {
  const contextValue = useMemo(
    () => ({ value, onValueChange }),
    [value, onValueChange]
  )

  return (
    <TabsContext.Provider value={contextValue}>
      <div className={className}>{children}</div>
    </TabsContext.Provider>
  )
}

export function TabsList({ className, children, ...props }) {
  return (
    <div
      className={clsx('inline-flex items-center gap-2 rounded-xl p-1', className)}
      role="tablist"
      {...props}
    >
      {children}
    </div>
  )
}

export function TabsTrigger({ value: triggerValue, className, children, ...props }) {
  const { value, onValueChange } = useTabsContext('TabsTrigger')
  const isActive = value === triggerValue

  return (
    <button
      type="button"
      role="tab"
      data-state={isActive ? 'active' : 'inactive'}
      aria-selected={isActive}
      className={clsx(
        'px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900 rounded-lg',
        isActive
          ? 'bg-primary text-primary-foreground shadow'
          : 'text-slate-300 hover:bg-slate-800/60 hover:text-slate-100',
        className
      )}
      onClick={() => onValueChange?.(triggerValue)}
      {...props}
    >
      {children}
    </button>
  )
}

export function TabsContent({ value: contentValue, className, children, ...props }) {
  const { value } = useTabsContext('TabsContent')
  if (value !== contentValue) {
    return null
  }

  return (
    <div
      role="tabpanel"
      className={className}
      {...props}
    >
      {children}
    </div>
  )
}
