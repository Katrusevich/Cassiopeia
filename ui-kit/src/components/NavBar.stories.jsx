import { CalendarDays, Clock, Globe, MessageCircle, PieChart, Calendar } from 'lucide-react';
import { NavBar } from './NavBar.jsx';

const items = [
  { id: 'today', label: 'Today', icon: Clock },
  { id: 'week', label: 'Week', icon: Calendar },
  { id: 'month', label: 'Month', icon: CalendarDays },
  { id: 'year', label: 'Year', icon: Globe },
  { id: 'wheel', label: 'Wheel', icon: PieChart },
  { id: 'chat', label: 'Chat', icon: MessageCircle },
];

export default {
  title: 'Components/NavBar',
  component: NavBar,
  args: { items, activeId: 'today' },
  argTypes: { activeId: { control: 'select', options: items.map((i) => i.id) } },
};

export const Playground = {};

/** Активний, hover і вимкнений пункти. */
export const States = {
  render: () => (
    <div style={{ display: 'grid', gap: 'var(--space-4)', maxWidth: 480 }}>
      <NavBar items={items} activeId="chat" />
      <NavBar items={items.map((i) => (i.id === 'year' ? { ...i, disabled: true } : i))} activeId="week" />
    </div>
  ),
};
