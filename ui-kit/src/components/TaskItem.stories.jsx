import { TaskItem } from './TaskItem.jsx';

export default {
  title: 'Components/TaskItem',
  component: TaskItem,
  args: { title: 'Finish the quarterly report', meta: 'Work · 90 min', time: '18:00' },
  decorators: [(Story) => <div style={{ maxWidth: 520 }}><Story /></div>],
};

export const Playground = { args: { onToggle: () => {}, onForward: () => {} } };

/** Стани завдання: todo / top 3 / done / pushed. */
export const AllStates = {
  render: () => (
    <div style={{ display: 'grid', gap: 'var(--space-3)', maxWidth: 520 }}>
      <TaskItem title="Call with the design team" meta="Work · 30 min" time="12:30" onToggle={() => {}} onForward={() => {}} />
      <TaskItem top title="Finish the quarterly report" meta="Top 3 · 90 min" time="18:00" onToggle={() => {}} onForward={() => {}} />
      <TaskItem status="done" title="Send invoice" meta="Admin · 10 min" time="09:00" onToggle={() => {}} />
      <TaskItem status="forwarded" title="Read the article" meta="Growth · 20 min" />
    </div>
  ),
};
