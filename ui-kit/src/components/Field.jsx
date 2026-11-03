import { useId } from 'react';
import { cx } from './cx.js';

/** Текстове поле. multiline → textarea. error показує повідомлення замість hint. */
export function Field({ label, hint, error, multiline, id, className, ...rest }) {
  const uid = useId();
  const fid = id || uid;
  const Control = multiline ? 'textarea' : 'input';
  const note = error || hint;
  return (
    <div className={cx('cs-field', error && 'cs-field--error')}>
      {label && (
        <label className="cs-field__label" htmlFor={fid}>
          {label}
        </label>
      )}
      <Control
        id={fid}
        className={cx('cs-field__control', className)}
        aria-invalid={error ? true : undefined}
        aria-describedby={note ? `${fid}-note` : undefined}
        {...rest}
      />
      {note && (
        <span id={`${fid}-note`} className="cs-field__hint">
          {note}
        </span>
      )}
    </div>
  );
}
