import { cx } from './cx.js';

/** value 0–100; tone: default | warning | error */
export function ProgressBar({ value, tone = 'default', label }) {
  const v = Math.max(0, Math.min(100, value));
  return (
    <div
      className={cx('cs-progress', tone !== 'default' && `cs-progress--${tone}`)}
      role="progressbar"
      aria-valuenow={Math.round(v)}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={label}
    >
      <div className="cs-progress__fill" style={{ width: `${v}%` }} />
    </div>
  );
}
