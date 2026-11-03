import { Badge } from './Badge.jsx';
import { ProgressBar } from './ProgressBar.jsx';
import { Toast } from './Toast.jsx';

export default { title: 'Components/Feedback' };

/** Semantic-кольори: success / warning / error (+ нейтральний і gold). */
export const Badges = {
  render: () => (
    <div style={{ display: 'flex', gap: 'var(--space-3)', flexWrap: 'wrap' }}>
      <Badge>neutral</Badge>
      <Badge tone="gold">gold</Badge>
      <Badge tone="success">success</Badge>
      <Badge tone="warning">warning</Badge>
      <Badge tone="error">error</Badge>
    </div>
  ),
};

export const Progress = {
  render: () => (
    <div style={{ display: 'grid', gap: 'var(--space-4)', maxWidth: 360 }}>
      <ProgressBar value={80} label="Efficiency" />
      <ProgressBar value={55} tone="warning" label="Efficiency" />
      <ProgressBar value={25} tone="error" label="Efficiency" />
    </div>
  ),
};

export const Toasts = {
  render: () => (
    <div style={{ display: 'grid', gap: 'var(--space-3)', maxWidth: 420 }}>
      <Toast action="Undo">Task pushed to the next slot</Toast>
      <Toast tone="success">3 tasks added to your day</Toast>
      <Toast tone="error" action="Retry">Could not push the task</Toast>
    </div>
  ),
};
