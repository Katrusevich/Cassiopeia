import { createContext, useCallback, useContext, useEffect, useMemo, useReducer, useRef } from 'react';
import { addDays, todayISO } from './dates.js';
import { defaultVision, seedTasks } from './mock.js';
import { parseMessage } from './parse.js';

const Ctx = createContext(null);

const greeting = {
  id: 'g',
  role: 'assistant',
  text: 'Hi! Tell me everything on your mind — tasks, deadlines, plans — and I’ll turn it into a plan for your day.',
};

function reducer(state, a) {
  switch (a.type) {
    case 'add':
      return { ...state, tasks: [...state.tasks, ...a.tasks] };
    case 'toggle':
      return {
        ...state,
        tasks: state.tasks.map((t) => (t.id === a.id ? { ...t, status: t.status === 'done' ? 'todo' : 'done' } : t)),
      };
    case 'forward':
      // Переносимо на наступний слот (завтра) і запам'ятовуємо стару дату для Undo.
      return {
        ...state,
        tasks: state.tasks.map((t) => (t.id === a.id ? { ...t, prevDate: t.date, date: addDays(t.date, 1) } : t)),
      };
    case 'undo':
      return {
        ...state,
        tasks: state.tasks.map((t) => (t.id === a.id && t.prevDate ? { ...t, date: t.prevDate, prevDate: undefined } : t)),
      };
    case 'chat':
      return { ...state, messages: [...state.messages, a.message] };
    case 'proposal':
      return { ...state, proposal: a.proposal };
    case 'vision':
      return { ...state, vision: a.text };
    case 'toast':
      return { ...state, toast: a.toast };
    default:
      return state;
  }
}

const EXAMPLE = 'Finish the report by 6 PM, call the client at 12:30 tomorrow, and gym in the evening';

function initialState(preset) {
  const base = { tasks: seedTasks(todayISO()), messages: [greeting], proposal: null, vision: defaultVision, toast: null };
  if (preset === 'plan') {
    // Знімок посеред сценарію: ШІ вже запропонував план, користувач його перевіряє.
    return {
      ...base,
      messages: [
        greeting,
        { id: 'u1', role: 'user', text: EXAMPLE },
        { id: 'a1', role: 'assistant', text: 'I found 3 tasks. Check the plan and adjust anything you like.' },
      ],
      proposal: parseMessage(EXAMPLE, todayISO()),
    };
  }
  return base;
}

/** preset: undefined | 'plan' — початковий стан для демонстрації (Storybook). */
export function AppProvider({ children, preset }) {
  const today = useMemo(() => todayISO(), []);
  const [state, dispatch] = useReducer(reducer, preset, initialState);

  const timer = useRef();
  const showToast = useCallback((toast) => {
    clearTimeout(timer.current);
    dispatch({ type: 'toast', toast });
    timer.current = setTimeout(() => dispatch({ type: 'toast', toast: null }), 5000);
  }, []);
  useEffect(() => () => clearTimeout(timer.current), []);

  const value = useMemo(
    () => ({ ...state, today, dispatch, showToast }),
    [state, today, showToast],
  );
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export const useApp = () => useContext(Ctx);
