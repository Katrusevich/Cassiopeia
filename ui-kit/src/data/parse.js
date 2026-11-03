import { addDays } from './dates.js';

// Імітація ШІ-розбору повідомлення. У справжньому продукті це робить модель;
// для прототипу достатньо евристик, щоб показати весь user flow.
const CATEGORIES = [
  ['Health', /gym|run|workout|training|yoga|doctor|dentist/i],
  ['Work', /report|call|meeting|email|demo|client|project|invoice/i],
  ['Finance', /budget|tax|pay\b|bank/i],
  ['Family', /mom|dad|parents|family|kids/i],
  ['Growth', /read|study|course|learn/i],
];

let seq = 100;

function pickTime(raw) {
  const ampm = raw.match(/\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b/i);
  if (ampm) {
    let h = Number(ampm[1]) % 12;
    if (/pm/i.test(ampm[3])) h += 12;
    return `${String(h).padStart(2, '0')}:${ampm[2] || '00'}`;
  }
  const hm = raw.match(/\b([01]?\d|2[0-3]):([0-5]\d)\b/);
  if (hm) return `${hm[1].padStart(2, '0')}:${hm[2]}`;
  if (/evening/i.test(raw)) return '19:00';
  if (/morning/i.test(raw)) return '09:00';
  return null;
}

const clean = (raw) => {
  const t = raw
    .replace(/^(also|then|and|i (need|have|want) to|need to|have to|want to|i'?ll|i will)\s+/i, '')
    .replace(/\b(by|at|before|around)\s+\d{1,2}(:\d{2})?\s*(am|pm)?/gi, '')
    .replace(/\b(today|tomorrow|in the evening|in the morning)\b/gi, '')
    .replace(/\s{2,}/g, ' ')
    .trim();
  return t.charAt(0).toUpperCase() + t.slice(1);
};

/** Повертає масив завдань; порожній масив = «ШІ не зрозумів, уточніть». */
export function parseMessage(text, today) {
  const parts = text
    .split(/[,;.\n]|\band\b|\bthen\b/i)
    .map((s) => s.trim())
    .filter((s) => s.split(/\s+/).length >= 2);
  return parts.slice(0, 6).map((raw, i) => {
    const category = CATEGORIES.find(([, re]) => re.test(raw))?.[0] || 'Personal';
    return {
      id: ++seq,
      title: clean(raw),
      date: /tomorrow/i.test(raw) ? addDays(today, 1) : today,
      time: pickTime(raw),
      duration: category === 'Work' ? 60 : 30,
      category,
      priority: /by|deadline|until|urgent|asap/i.test(raw) ? 1 : i === 0 ? 2 : 3,
      status: 'todo',
    };
  });
}
