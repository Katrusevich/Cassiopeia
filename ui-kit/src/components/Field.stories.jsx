import { Field } from './Field.jsx';

export default {
  title: 'Components/Input',
  component: Field,
  args: { label: 'Task title', placeholder: 'What needs to be done?' },
};

export const Playground = {};

/** Усі стани поля: default / hover / focus / error / disabled. */
export const AllStates = {
  render: () => (
    <div style={{ display: 'grid', gap: 'var(--space-5)', maxWidth: 360 }}>
      <Field label="Default" placeholder="Type here" />
      <Field label="Hover" placeholder="Type here" className="is-hover" />
      <Field label="Focus" placeholder="Type here" className="is-focus" hint="Press Enter to save" />
      <Field label="Error" defaultValue="" placeholder="Type here" error="Title can’t be empty" />
      <Field label="Disabled" placeholder="Type here" disabled />
    </div>
  ),
};

export const Textarea = {
  args: { label: 'Vision & Mission', multiline: true, placeholder: 'What are you working toward, and why?' },
};
