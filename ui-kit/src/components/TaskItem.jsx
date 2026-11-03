import { Check, FastForward } from 'lucide-react';
import { Badge } from './Badge.jsx';
import { Button } from './Button.jsx';
import { cx } from './cx.js';

/** status: todo | done | forwarded. top = завдання з Top 3. */
export function TaskItem({ title, meta, time, status = 'todo', top, onToggle, onForward }) {
  const done = status === 'done';
  return (
    <div className={cx('cs-task', top && 'cs-task--top', done && 'cs-task--done', status === 'forwarded' && 'cs-task--forwarded')}>
      <button
        type="button"
        className="cs-task__check"
        aria-label={done ? 'Mark as not done' : 'Mark as done'}
        aria-pressed={done}
        disabled={!onToggle || status === 'forwarded'}
        onClick={onToggle}
      >
        {done && <Check size={16} aria-hidden="true" />}
      </button>
      <div className="cs-task__body">
        <div className="cs-task__title">{title}</div>
        {meta && <div className="cs-task__meta">{meta}</div>}
      </div>
      <div className="cs-task__actions">
        {time && <Badge tone={top ? 'gold' : 'neutral'}>{time}</Badge>}
        {onForward && !done && status !== 'forwarded' && (
          <Button variant="ghost" size="sm" icon={FastForward} onClick={onForward} aria-label={`Push ${title} to the next slot`} />
        )}
        {status === 'forwarded' && <Badge tone="warning">Pushed</Badge>}
      </div>
    </div>
  );
}
