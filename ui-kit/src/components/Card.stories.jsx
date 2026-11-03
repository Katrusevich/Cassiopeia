import { Button } from './Button.jsx';
import { Card } from './Card.jsx';

export default {
  title: 'Components/Card',
  component: Card,
  argTypes: { variant: { control: 'select', options: ['default', 'elevated', 'accent'] } },
};

export const Playground = {
  args: { title: 'Today’s focus', children: <p>Three tasks that matter most today.</p> },
};

/** Варіанти картки та інтерактивний hover-стан. */
export const Variants = {
  render: () => (
    <div style={{ display: 'grid', gap: 'var(--space-4)', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))' }}>
      <Card title="Default">
        <p className="t-small t-muted">Basic surface for grouped content.</p>
      </Card>
      <Card variant="elevated" title="Elevated">
        <p className="t-small t-muted">Raised surface with a soft shadow.</p>
      </Card>
      <Card variant="accent" title="Accent">
        <p className="t-small t-muted">Highlights the most important block.</p>
      </Card>
      <Card interactive title="Interactive">
        <p className="t-small t-muted">Hover to see the state.</p>
      </Card>
      <Card interactive className="is-hover" title="Interactive · hover">
        <p className="t-small t-muted">Forced hover state.</p>
      </Card>
      <Card title="With actions" footer={<><Button size="sm">Confirm</Button><Button size="sm" variant="outline">Edit</Button></>}>
        <p className="t-small t-muted">Footer holds the actions.</p>
      </Card>
    </div>
  ),
};
