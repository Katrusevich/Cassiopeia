import { addDays } from './dates.js';

/** Початкові завдання; дати рахуються від сьогодні, щоб прототип завжди виглядав «живим». */
export const seedTasks = (today) => [
  { id: 1, title: 'Prepare the product demo', date: today, time: '10:00', duration: 60, category: 'Work', priority: 1, status: 'todo' },
  { id: 2, title: 'Reply to investor emails', date: today, time: '11:30', duration: 30, category: 'Work', priority: 2, status: 'todo' },
  { id: 3, title: 'Team sync', date: today, time: '14:00', duration: 30, category: 'Work', priority: 2, status: 'todo' },
  { id: 4, title: 'Evening run', date: today, time: '19:00', duration: 45, category: 'Health', priority: 3, status: 'todo' },
  { id: 5, title: 'Send the invoice', date: today, time: '09:00', duration: 10, category: 'Work', priority: 3, status: 'done' },
  { id: 6, title: 'Dentist appointment', date: addDays(today, 1), time: '09:30', duration: 60, category: 'Health', priority: 2, status: 'todo' },
  { id: 7, title: 'Plan the Q1 budget', date: addDays(today, 2), time: '11:00', duration: 90, category: 'Finance', priority: 1, status: 'todo' },
  { id: 8, title: 'Call the parents', date: addDays(today, 3), time: '18:00', duration: 30, category: 'Family', priority: 3, status: 'todo' },
  { id: 9, title: 'Read 20 pages', date: addDays(today, 4), time: '21:00', duration: 30, category: 'Growth', priority: 3, status: 'todo' },
  { id: 10, title: 'Quarterly review', date: addDays(today, 9), time: '15:00', duration: 90, category: 'Work', priority: 1, status: 'todo' },
  { id: 11, title: 'Yoga class', date: addDays(today, 12), time: '08:00', duration: 60, category: 'Health', priority: 3, status: 'todo' },
  { id: 12, title: 'Renew the passport', date: addDays(today, 20), time: null, duration: 45, category: 'Personal', priority: 2, status: 'todo' },
];

// Вісім сфер і шкала 1–9 — як у PRD та в основному застосунку (core/config.py → wheel_categories).
export const WHEEL_MAX = 9;

export const wheelData = [
  { label: 'Health', value: 4 },
  { label: 'Relationships', value: 7 },
  { label: 'Environment', value: 6 },
  { label: 'Career & Purpose', value: 8 },
  { label: 'Finances', value: 6 },
  { label: 'Personal Growth', value: 5 },
  { label: 'Fun & Recreation', value: 3 },
  { label: 'Spirituality', value: 5 },
];

// Підказки дій — ті самі, що в CATEGORY_META основного застосунку (static/js/app.js).
export const wheelActions = {
  Health: 'Regular Exercise',
  Relationships: 'Family Time',
  Environment: 'Improve Environment',
  'Career & Purpose': 'Career Advancement',
  Finances: 'Financial Planning',
  'Personal Growth': 'Personal Development',
  'Fun & Recreation': 'Make Time to Recharge',
  Spirituality: 'Spiritual Practice',
};

export const trackerRows = [
  { id: 1, title: 'Prepare the product demo', type: 'Deep work', estimated: 60, actual: 75 },
  { id: 2, title: 'Reply to investor emails', type: 'Admin', estimated: 30, actual: 32 },
  { id: 3, title: 'Team sync', type: 'Meeting', estimated: 30, actual: 55 },
  { id: 4, title: 'Dentist appointment', type: 'Errand', estimated: 60, actual: 60 },
];

export const defaultVision =
  'I plan every day to build a calm, focused life: meaningful work, enough rest, and time for the people I love.';
