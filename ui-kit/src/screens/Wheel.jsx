import { ArrowLeft, Compass, LineChart, Sparkles } from 'lucide-react';
import { useState } from 'react';
import { Badge, BalanceWheel, Button, Card, Field, ProgressBar } from '../components/index.js';
import { trackerRows, wheelActions, wheelData } from '../data/mock.js';
import { useApp } from '../data/store.jsx';

const Back = ({ navigate }) => (
  <Button variant="ghost" size="sm" icon={ArrowLeft} onClick={() => navigate('wheel')}>
    Back to Wheel
  </Button>
);

export function Wheel({ navigate }) {
  const [insights, setInsights] = useState(false);
  const weakest = [...wheelData].sort((a, b) => a.value - b.value).slice(0, 3);
  return (
    <div className="stack stack--lg">
      <header className="screen-head">
        <div>
          <p className="t-eyebrow">Your balance</p>
          <h1 className="t-h1">Wheel of Balance</h1>
        </div>
      </header>

      <Card variant="elevated">
        <BalanceWheel data={wheelData} />
        <p className="t-small t-muted" style={{ textAlign: 'center' }}>
          Rest and Health need attention this week.
        </p>
      </Card>

      <section className="stack">
        <h2 className="t-h2">Priority Board</h2>
        {weakest.map((w, i) => (
          <Card key={w.label}>
            <div className="row-between">
              <span className="t-h3">{i + 1}. {w.label}</span>
              <Badge tone={w.value <= 3 ? 'error' : 'warning'}>{w.value}/10</Badge>
            </div>
            <p className="t-small t-muted" style={{ marginTop: 'var(--space-2)' }}>
              {wheelActions[w.label]}
            </p>
          </Card>
        ))}
      </section>

      {insights && (
        <Card variant="accent" title="AI insights">
          <p className="t-small">
            Most of your tasks this week are work-related. Moving one task to tomorrow frees an evening for rest, which is
            your weakest area right now.
          </p>
        </Card>
      )}

      <div className="stack">
        <Button block icon={Sparkles} onClick={() => setInsights((v) => !v)}>
          {insights ? 'Hide' : 'AI insights & recommendations'}
        </Button>
        <Button block variant="outline" icon={Compass} onClick={() => navigate('vision')}>
          Vision &amp; Mission
        </Button>
        <Button block variant="secondary" icon={LineChart} onClick={() => navigate('tracker')}>
          Task Tracker
        </Button>
      </div>
    </div>
  );
}

export function Vision({ navigate }) {
  const { vision, dispatch, showToast } = useApp();
  const [draft, setDraft] = useState(vision);
  const empty = !draft.trim();
  return (
    <div className="stack stack--lg">
      <Back navigate={navigate} />
      <header className="screen-head">
        <div>
          <p className="t-eyebrow">Why you plan</p>
          <h1 className="t-h1">Vision &amp; Mission</h1>
        </div>
      </header>
      <p className="t-small t-muted">The core reminder of why you plan every day — read it before you start.</p>
      <Field
        multiline
        rows={6}
        aria-label="Vision and mission"
        placeholder="What are you working toward, and why does it matter?"
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        error={empty ? 'Write a few words — they will be shown every morning' : undefined}
      />
      <Button
        disabled={empty}
        onClick={() => {
          dispatch({ type: 'vision', text: draft.trim() });
          showToast({ text: 'Vision saved', tone: 'success' });
        }}
      >
        Save
      </Button>
    </div>
  );
}

export function Tracker({ navigate }) {
  return (
    <div className="stack stack--lg">
      <Back navigate={navigate} />
      <header className="screen-head">
        <div>
          <p className="t-eyebrow">Time &amp; efficiency</p>
          <h1 className="t-h1">Task Tracker</h1>
        </div>
      </header>
      {trackerRows.map((r) => {
        const pct = Math.min(100, (r.estimated / r.actual) * 100);
        const tone = pct < 60 ? 'error' : pct < 90 ? 'warning' : 'default';
        return (
          <Card key={r.id}>
            <div className="row-between">
              <span className="t-h3">{r.title}</span>
              <Badge>{r.type}</Badge>
            </div>
            <div style={{ margin: 'var(--space-3) 0 var(--space-2)' }}>
              <ProgressBar value={pct} tone={tone} label={`${r.title} efficiency`} />
            </div>
            <p className="t-caption">
              {r.actual} min actual vs {r.estimated} min estimated · {Math.round(pct)}% efficiency
            </p>
          </Card>
        );
      })}
    </div>
  );
}
