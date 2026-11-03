import { Calendar, CalendarDays, Clock, Globe, MessageCircle, PieChart } from 'lucide-react';
import { useEffect, useState } from 'react';
import { NavBar, Toast } from '../components/index.js';
import { AppProvider, useApp } from '../data/store.jsx';
import { Month, Week, Year } from './Calendar.jsx';
import { Chat } from './Chat.jsx';
import { Today } from './Today.jsx';
import { Tracker, Vision, Wheel } from './Wheel.jsx';

const NAV = [
  { id: 'today', label: 'Today', icon: Clock },
  { id: 'week', label: 'Week', icon: Calendar },
  { id: 'month', label: 'Month', icon: CalendarDays },
  { id: 'year', label: 'Year', icon: Globe },
  { id: 'wheel', label: 'Wheel', icon: PieChart },
  { id: 'chat', label: 'Chat', icon: MessageCircle },
];

const SCREENS = { today: Today, week: Week, month: Month, year: Year, wheel: Wheel, chat: Chat, vision: Vision, tracker: Tracker };
// Vision і Tracker — підсторінки Wheel (див. sitemap), тому в навігації підсвічується Wheel.
const NAV_OF = { vision: 'wheel', tracker: 'wheel' };

function Shell({ initialScreen, syncHash }) {
  const [screen, setScreen] = useState(initialScreen);
  const { toast } = useApp();
  const Screen = SCREENS[screen];

  useEffect(() => {
    if (syncHash) window.location.hash = screen;
    window.scrollTo?.(0, 0);
  }, [screen, syncHash]);

  return (
    <div className="app">
      <main className="app__main">
        <Screen navigate={setScreen} />
      </main>
      {toast && (
        <div className="app__toast">
          <Toast tone={toast.tone} action={toast.action} onAction={toast.onAction}>
            {toast.text}
          </Toast>
        </div>
      )}
      <div className="app__nav">
        <NavBar items={NAV} activeId={NAV_OF[screen] || screen} onChange={setScreen} />
      </div>
    </div>
  );
}

/** Клікабельний прототип. initialScreen — з якого екрана стартувати; syncHash — писати екран у #hash. */
export function App({ initialScreen, syncHash = false, preset }) {
  const fromHash = typeof window !== 'undefined' ? window.location.hash.slice(1) : '';
  const start = initialScreen || (SCREENS[fromHash] ? fromHash : 'today');
  return (
    <AppProvider preset={preset}>
      <Shell initialScreen={start} syncHash={syncHash} />
    </AppProvider>
  );
}
