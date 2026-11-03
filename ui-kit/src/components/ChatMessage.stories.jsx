import { ChatMessage } from './ChatMessage.jsx';

export default { title: 'Components/ChatMessage', component: ChatMessage };

export const Conversation = {
  render: () => (
    <div style={{ display: 'grid', gap: 'var(--space-3)', maxWidth: 480 }}>
      <ChatMessage role="assistant">Hi! Tell me everything on your mind — I’ll turn it into a plan.</ChatMessage>
      <ChatMessage role="user">Finish the report by 6 PM, call at 12:30 tomorrow, and gym in the evening.</ChatMessage>
      <ChatMessage role="assistant" typing />
    </div>
  ),
};
