import { Send, Trash2 } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { Badge, Button, Card, ChatMessage, Field } from '../components/index.js';
import { fmt } from '../data/dates.js';
import { parseMessage } from '../data/parse.js';
import { useApp } from '../data/store.jsx';

const EXAMPLE = 'Finish the report by 6 PM, call the client at 12:30 tomorrow, and gym in the evening';

export function Chat({ navigate }) {
  const { messages, proposal, today, dispatch, showToast } = useApp();
  const [text, setText] = useState('');
  const [thinking, setThinking] = useState(false);
  const timer = useRef();
  const endRef = useRef();

  useEffect(() => () => clearTimeout(timer.current), []);
  useEffect(() => {
    endRef.current?.scrollIntoView?.({ block: 'end' });
  }, [messages, proposal, thinking]);

  const send = (e) => {
    e?.preventDefault();
    const value = text.trim();
    if (!value || thinking) return;
    dispatch({ type: 'chat', message: { id: Date.now(), role: 'user', text: value } });
    dispatch({ type: 'proposal', proposal: null });
    setText('');
    setThinking(true);
    // Імітуємо роботу ШІ: розпізнано завдання → картка плану, інакше — прохання уточнити.
    timer.current = setTimeout(() => {
      const tasks = parseMessage(value, today);
      setThinking(false);
      if (tasks.length) {
        dispatch({ type: 'chat', message: { id: Date.now() + 1, role: 'assistant', text: `I found ${tasks.length} task${tasks.length > 1 ? 's' : ''}. Check the plan and adjust anything you like.` } });
        dispatch({ type: 'proposal', proposal: tasks });
      } else {
        dispatch({ type: 'chat', message: { id: Date.now() + 1, role: 'assistant', text: 'I couldn’t find a task in that. What exactly needs to be done, and by when?' } });
      }
    }, 900);
  };

  const edit = (id, title) => dispatch({ type: 'proposal', proposal: proposal.map((t) => (t.id === id ? { ...t, title } : t)) });
  const remove = (id) => dispatch({ type: 'proposal', proposal: proposal.filter((t) => t.id !== id) });

  const confirm = () => {
    const tasks = proposal.filter((t) => t.title.trim());
    dispatch({ type: 'add', tasks });
    dispatch({ type: 'proposal', proposal: null });
    dispatch({ type: 'chat', message: { id: Date.now(), role: 'assistant', text: 'Done — your plan is on the Today screen.' } });
    showToast({ text: `${tasks.length} task${tasks.length > 1 ? 's' : ''} added to your day`, tone: 'success' });
    navigate('today');
  };

  return (
    <div className="chat">
      <header className="screen-head">
        <div>
          <p className="t-eyebrow">AI planner</p>
          <h1 className="t-h1">Chat</h1>
        </div>
      </header>

      <div className="chat__log" aria-live="polite">
        {messages.map((m) => (
          <ChatMessage key={m.id} role={m.role}>
            {m.text}
          </ChatMessage>
        ))}
        {thinking && <ChatMessage typing />}

        {proposal && (
          <Card variant="accent" title="Your plan">
            <div className="stack">
              {proposal.length === 0 && <p className="t-small t-muted">No tasks left in the plan.</p>}
              {proposal.map((t) => (
                <div key={t.id} className="proposal-row">
                  <Field aria-label="Task title" value={t.title} onChange={(e) => edit(t.id, e.target.value)} error={t.title.trim() ? undefined : 'Title can’t be empty'} />
                  <div className="proposal-row__meta">
                    <Badge tone="gold">{t.time || 'any time'}</Badge>
                    <Badge>{fmt(t.date, { weekday: 'short', day: 'numeric', month: 'short' })}</Badge>
                    <Badge tone={t.priority === 1 ? 'error' : 'neutral'}>P{t.priority}</Badge>
                    <Button variant="ghost" size="sm" icon={Trash2} aria-label={`Remove ${t.title}`} onClick={() => remove(t.id)} />
                  </div>
                </div>
              ))}
            </div>
            <div className="cs-card__footer">
              <Button onClick={confirm} disabled={!proposal.some((t) => t.title.trim())}>
                Add to my day
              </Button>
              <Button variant="ghost" onClick={() => dispatch({ type: 'proposal', proposal: null })}>
                Discard
              </Button>
            </div>
          </Card>
        )}
        <div ref={endRef} />
      </div>

      <form className="chat__composer" onSubmit={send}>
        <Field
          multiline
          aria-label="Message"
          placeholder="Tell me what’s on your mind…"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) send(e);
          }}
          rows={2}
        />
        <div className="row-between">
          <Button variant="ghost" size="sm" onClick={() => setText(EXAMPLE)}>
            Use an example
          </Button>
          <Button type="submit" icon={Send} disabled={!text.trim() || thinking}>
            Send
          </Button>
        </div>
      </form>
    </div>
  );
}
