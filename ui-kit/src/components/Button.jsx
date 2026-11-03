import { cx } from './cx.js';

/** variant: primary | secondary | outline | ghost | danger; size: sm | md | lg */
export function Button({ variant = 'primary', size = 'md', block, icon: Icon, className, children, ...rest }) {
  return (
    <button
      type="button"
      className={cx('cs-btn', `cs-btn--${variant}`, size !== 'md' && `cs-btn--${size}`, block && 'cs-btn--block', className)}
      {...rest}
    >
      {Icon && <Icon size={16} aria-hidden="true" />}
      {children}
    </button>
  );
}
