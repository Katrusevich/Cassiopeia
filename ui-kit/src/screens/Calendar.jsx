import { useState } from 'react';
import { Badge, Card, TaskItem } from '../components/index.js';
import { addDays, fmt, fromISO, toISO } from '../data/dates.js';
import { useApp } from '../data/store.jsx';

const sorted = (list) => [...list].sort((a, b) => (a.time || '99').localeCompare(b.time || '99'));
const rowMeta = (t) => `${t.category} · ${t.duration} min`;

function DayList({ date, tasks }) {
  const list = sorted(tasks.filter((t) => t.date === date));
  if (!list.length) return <p className="t-small t-muted">Nothing planned.</p>;
  return (
    <div className="stack">
      {list.map((t) => (
        <TaskItem key={t.id} title={t.title} meta={rowMeta(t)} time={t.time} status={t.status} />
      ))}
    </div>
  );
}

/** Week: сім днів від сьогодні. */
export function Week() {
  const { tasks, today } = useApp();
  return (
    <div className="stack stack--lg">
      <header className="screen-head">
        <div>
          <p className="t-eyebrow">Next 7 days</p>
          <h1 className="t-h1">Week</h1>
        </div>
      </header>
      {Array.from({ length: 7 }, (_, i) => addDays(today, i)).map((d, i) => {
        const count = tasks.filter((t) => t.date === d).length;
        return (
          <Card key={d} variant={i === 0 ? 'accent' : 'default'}>
            <div className="row-between" style={{ marginBottom: 'var(--space-3)' }}>
              <h2 className="t-h3">{i === 0 ? 'Today' : fmt(d, { weekday: 'long', day: 'numeric', month: 'short' })}</h2>
              <Badge tone={count ? 'gold' : 'neutral'}>{count} task{count === 1 ? '' : 's'}</Badge>
            </div>
            <DayList date={d} tasks={tasks} />
          </Card>
        );
      })}
    </div>
  );
}

/** Month: сітка поточного місяця; тап по дню показує його завдання (екран Day). */
export function Month() {
  const { tasks, today } = useApp();
  const [selected, setSelected] = useState(today);
  const first = fromISO(today);
  first.setDate(1);
  const offset = (first.getDay() + 6) % 7; // тиждень починається з понеділка
  const days = new Date(first.getFullYear(), first.getMonth() + 1, 0).getDate();
  const cells = [...Array(offset).fill(null), ...Array.from({ length: days }, (_, i) => {
    const d = new Date(first.getFullYear(), first.getMonth(), i + 1);
    return toISO(d);
  })];

  return (
    <div className="stack stack--lg">
      <header className="screen-head">
        <div>
          <p className="t-eyebrow">{fmt(today, { year: 'numeric' })}</p>
          <h1 className="t-h1">{fmt(today, { month: 'long' })}</h1>
        </div>
      </header>
      <Card>
        <div className="cal">
          {['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'].map((d) => (
            <span key={d} className="cal__dow">{d}</span>
          ))}
          {cells.map((d, i) =>
            d ? (
              <button
                key={d}
                type="button"
                className="cal__day"
                data-today={d === today || undefined}
                aria-pressed={d === selected}
                onClick={() => setSelected(d)}
              >
                {Number(d.slice(8))}
                {tasks.some((t) => t.date === d) && <i className="cal__dot" />}
              </button>
            ) : (
              <span key={`e${i}`} />
            ),
          )}
        </div>
      </Card>
      <Card title={fmt(selected, { weekday: 'long', day: 'numeric', month: 'long' })}>
        <DayList date={selected} tasks={tasks} />
      </Card>
    </div>
  );
}

/** Year: 12 плиток із кількістю завдань; тап → Month. */
export function Year({ navigate }) {
  const { tasks, today } = useApp();
  const year = fromISO(today).getFullYear();
  return (
    <div className="stack stack--lg">
      <header className="screen-head">
        <div>
          <p className="t-eyebrow">Big picture</p>
          <h1 className="t-h1">{year}</h1>
        </div>
      </header>
      <div className="year">
        {Array.from({ length: 12 }, (_, m) => {
          const count = tasks.filter((t) => fromISO(t.date).getFullYear() === year && fromISO(t.date).getMonth() === m).length;
          const current = fromISO(today).getMonth() === m;
          return (
            <Card key={m} interactive variant={current ? 'accent' : 'default'} onClick={() => navigate('month')} role="button" tabIndex={0}
              onKeyDown={(e) => { if (e.key === 'Enter') navigate('month'); }}>
              <p className="t-h3">{new Date(year, m, 1).toLocaleDateString('en-GB', { month: 'long' })}</p>
              <p className="t-caption">{count ? `${count} task${count === 1 ? '' : 's'}` : 'No tasks'}</p>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
