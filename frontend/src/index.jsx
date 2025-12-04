/**
 * Application Entry Point
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

// Get root element
const container = document.getElementById('root');

// Create root
const root = createRoot(container);

// Render app
root.render(
  <StrictMode>
    <App />
  </StrictMode>,
);



