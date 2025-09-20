import { forwardRef } from 'react'
import { clsx } from 'clsx'

export const Button = forwardRef(({ className, variant = 'primary', size = 'md', ...props }, ref) => {
  return (
    <button
      ref={ref}
      className={clsx(
        'inline-flex items-center justify-center rounded-lg font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
        {
          // Variants
          'bg-primary text-primary-foreground hover:bg-primary/90': variant === 'primary',
          'bg-secondary text-secondary-foreground hover:bg-secondary/80': variant === 'secondary',
          'border border-input bg-background hover:bg-accent hover:text-accent-foreground': variant === 'outline',
          'hover:bg-accent hover:text-accent-foreground': variant === 'ghost',
          // Sizes
          'h-10 px-4 py-2 text-sm': size === 'sm',
          'h-10 px-8 text-base': size === 'md',
          'h-11 px-8 text-lg': size === 'lg',
        },
        className
      )}
      {...props}
    />
  )
})
Button.displayName = 'Button'

export const Input = forwardRef(({ className, type = 'text', ...props }, ref) => {
  return (
    <input
      type={type}
      ref={ref}
      className={clsx(
        'flex h-10 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-400 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 disabled:cursor-not-allowed disabled:opacity-50',
        className
      )}
      {...props}
    />
  )
})
Input.displayName = 'Input'

export const Select = forwardRef(({ className, children, ...props }, ref) => {
  return (
    <select
      ref={ref}
      className={clsx(
        'flex h-10 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 disabled:cursor-not-allowed disabled:opacity-50',
        className
      )}
      {...props}
    >
      {children}
    </select>
  )
})
Select.displayName = 'Select'

export const Badge = forwardRef(({ className, variant = 'default', ...props }, ref) => {
  return (
    <div
      ref={ref}
      className={clsx(
        'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2',
        {
          'border-slate-600 bg-slate-800 text-slate-300': variant === 'default',
        },
        className
      )}
      {...props}
    />
  )
})
Badge.displayName = 'Badge'

export const Modal = ({ children, onClose }) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      <div className="relative z-50 bg-slate-800 rounded-xl border border-slate-700 shadow-xl max-w-md w-full mx-4">
        {children}
      </div>
    </div>
  )
}
