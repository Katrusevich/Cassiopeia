import { cx } from './cx.js';

/** tone: default | success | error; action — підпис дії (наприклад, Undo). */
export function Toast({ tone = 'default', action, onAction, children }) {
  return (
    <div className={cx('cs-toast', tone !== 'default' && `cs-toast--${tone}`)} role="status">
      <span>{children}</span>
      {action && (
        <button type="button" className="cs-toast__action" onClick={onAction}>
          {action}
        </button>
      )}
    </div>
  );
}
