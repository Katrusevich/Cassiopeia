import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './styles/tokens.css';
import './styles/base.css';
import './components/components.css';
import './screens/screens.css';
import { App } from './screens/App.jsx';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App syncHash />
  </StrictMode>,
);
