import { useEffect } from 'react';
import '../src/styles/tokens.css';
import '../src/styles/base.css';
import '../src/components/components.css';
import '../src/screens/screens.css';

// Перемикач теми в тулбарі Storybook: міняє data-theme на <html>.
// Це демонстрація вимоги реюзабельності — вся тема живе в tokens.css.
export const globalTypes = {
  theme: {
    description: 'Тема (кольори з tokens.css)',
    toolbar: {
      title: 'Theme',
      icon: 'paintbrush',
      items: [
        { value: 'classic', title: 'Old Money (navy)' },
        { value: 'forest', title: 'Forest (green)' },
      ],
      dynamicTitle: true,
    },
  },
};
export const initialGlobals = { theme: 'classic' };

const withTheme = (Story, context) => {
  const theme = context.globals.theme || 'classic';
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);
  return <Story />;
};

export const decorators = [withTheme];
export const parameters = {
  layout: 'padded',
  backgrounds: { disable: true },
  controls: { expanded: true },
};
