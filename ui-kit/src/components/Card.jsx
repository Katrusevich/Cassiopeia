import { cx } from './cx.js';

/** variant: default | elevated | accent; interactive додає hover-стан. */
export function Card({ variant = 'default', interactive, title, footer, className, children, ...rest }) {
  return (
    <div
      className={cx('cs-card', variant !== 'default' && `cs-card--${variant}`, interactive && 'cs-card--interactive', className)}
      {...rest}
    >
      {title && <h3 className="t-h3 cs-card__title">{title}</h3>}
      {children}
      {footer && <div className="cs-card__footer">{footer}</div>}
    </div>
  );
}
