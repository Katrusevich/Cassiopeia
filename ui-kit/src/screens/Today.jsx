import { MessageCircle, Plus } from 'lucide-react';
import { useState } from 'react';
import { Badge, Button, Card, Field, ProgressBar, TaskItem } from '../components/index.js';
import { fmt } from '../data/dates.js';
import { useApp } from '../data/store.jsx';

const byPriority = (a, b) => a.priority - b.priority || (a.time || '99').localeCompare(b.time || '99');
const meta = (t) => `${t.category} · ${t.duration} min`;

export function Today({ navigate }) {
  const { tasks, today, dispatch, showToast } = useApp();
  const [title, setTitle] = useState('');
  const todays = tasks.filter((t) => t.date === today);
  const open = todays.filter((t) => t.status !== 'done').sort(byPriority);
  const top = open.slice(0, 3);
  const rest = [...open.slice(3), ...todays.filter((t) => t.status === 'done')];
  const doneCount = todays.filter((t) => t.status === 'done').length;

  const forward = (t) => {
    dispatch({ type: 'forward', id: t.id });
    showToast({ text: `“${t.title}” pushed to the next slot`, action: 'Undo', onAction: () => dispatch({ type: 'undo', id: t.id }) });
  };

  const quickAdd = (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    dispatch({ type: 'add', tasks: [{ id: Date.now(), title: title.trim(), date: today, time: null, duration: 30, category: 'Personal', priority: 3, status: 'todo' }] });
    setTitle('');
  };

  const row = (t, isTop) => (
    <TaskItem
      key={t.id}
      top={isTop}
      title={t.title}
      meta={isTop ? `Top 3 · ${meta(t)}` : meta(t)}
      time={t.time}
      status={t.status}
      onToggle={() => dispatch({ type: 'toggle', id: t.id })}
      onForward={() => forward(t)}
    />
  );

  return (
    <div className="stack stack--lg">
      <header className="screen-head">
        <div>
          <p className="t-eyebrow">{fmt(today, { weekday: 'long', day: 'numeric', month: 'long' })}</p>
          <h1 className="t-h1">Today</h1>
        </div>
        <Button variant="outline" size="sm" icon={MessageCircle} onClick={() => navigate('chat')}>
          Plan with chat
        </Button>
      </header>

      {todays.length === 0 ? (
        <Card variant="accent" title="Nothing planned yet">
          <p className="t-small t-muted">Write what’s on your mind in the chat and I’ll build the day for you.</p>
          <div className="cs-card__footer">
            <Button onClick={() => navigate('chat')}>Plan with chat</Button>
          </div>
        </Card>
      ) : (
        <>
          <Card>
            <div className="row-between">
              <span className="t-small">
                <b>{doneCount}</b> of {todays.length} done
              </span>
              <Badge tone="gold">{Math.round((doneCount / todays.length) * 100)}%</Badge>
            </div>
            <div style={{ marginTop: 'var(--space-3)' }}>
              <ProgressBar value={(doneCount / todays.length) * 100} label="Day progress" />
            </div>
          </Card>

          <section className="stack">
            <h2 className="t-h2">Top 3</h2>
            {top.length ? top.map((t) => row(t, true)) : <p className="t-small t-muted">All done — enjoy your evening.</p>}
          </section>

          {rest.length > 0 && (
            <section className="stack">
              <h2 className="t-h2">The rest of the day</h2>
              {rest.map((t) => row(t, false))}
            </section>
          )}
        </>
      )}

      <form className="quick-add" onSubmit={quickAdd}>
        <Field aria-label="Quick add" placeholder="Quick add a task…" value={title} onChange={(e) => setTitle(e.target.value)} />
        <Button type="submit" icon={Plus} disabled={!title.trim()}>
          Add
        </Button>
      </form>
    </div>
  );
}
