import { cx } from './cx.js';

/** role: user | assistant; typing показує індикатор «ШІ думає». */
export function ChatMessage({ role = 'assistant', typing, children }) {
  return (
    <div className={cx('cs-msg', `cs-msg--${role}`)}>
      <div className="cs-msg__bubble">
        {typing ? (
          <span className="cs-typing" role="status" aria-label="Assistant is typing">
            <i />
            <i />
            <i />
          </span>
        ) : (
          children
        )}
      </div>
    </div>
  );
}
