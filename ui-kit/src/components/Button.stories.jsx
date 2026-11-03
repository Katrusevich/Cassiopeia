import { Plus } from 'lucide-react';
import { Button } from './Button.jsx';

export default {
  title: 'Components/Button',
  component: Button,
  argTypes: {
    variant: { control: 'select', options: ['primary', 'secondary', 'outline', 'ghost', 'danger'] },
    size: { control: 'select', options: ['sm', 'md', 'lg'] },
    disabled: { control: 'boolean' },
  },
  args: { children: 'Add to my day', variant: 'primary', size: 'md' },
};

export const Playground = {};

const variants = ['primary', 'secondary', 'outline', 'ghost', 'danger'];
const states = [
  ['Default', {}],
  ['Hover', { className: 'is-hover' }],
  ['Active', { className: 'is-active' }],
  ['Focus', { className: 'is-focus' }],
  ['Disabled', { disabled: true }],
];

/** Усі варіанти у всіх станах: default / hover / active / focus / disabled. */
export const AllStates = {
  render: () => (
    <table style={{ borderCollapse: 'separate', borderSpacing: 'var(--space-3)' }}>
      <thead>
        <tr>
          <th />
          {states.map(([name]) => (
            <th key={name} className="t-caption" style={{ textAlign: 'left' }}>
              {name}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {variants.map((v) => (
          <tr key={v}>
            <td className="t-caption">{v}</td>
            {states.map(([name, props]) => (
              <td key={name}>
                <Button variant={v} {...props}>
                  Button
                </Button>
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  ),
};

export const Sizes = {
  render: () => (
    <div style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'center' }}>
      <Button size="sm">Small</Button>
      <Button size="md">Medium</Button>
      <Button size="lg">Large</Button>
    </div>
  ),
};

export const WithIcon = { args: { icon: Plus, children: 'Quick add' } };
