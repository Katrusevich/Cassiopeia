import { cx } from './cx.js';

/** tone: neutral | gold | success | warning | error */
export function Badge({ tone = 'neutral', children }) {
  return <span className={cx('cs-badge', tone !== 'neutral' && `cs-badge--${tone}`)}>{children}</span>;
}
