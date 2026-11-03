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

export const wheelData = [
  { label: 'Career', value: 8 },
  { label: 'Health', value: 4 },
  { label: 'Finance', value: 6 },
  { label: 'Family', value: 7 },
  { label: 'Growth', value: 5 },
  { label: 'Rest', value: 3 },
];

export const wheelActions = {
  Rest: 'Block one free evening this week.',
  Health: 'Schedule two workouts for the next days.',
  Growth: 'Add 20 minutes of reading to today.',
  Finance: 'Review this month’s expenses.',
  Family: 'Plan a call with someone close.',
  Career: 'Keep the current pace.',
};

export const trackerRows = [
  { id: 1, title: 'Prepare the product demo', type: 'Deep work', estimated: 60, actual: 75 },
  { id: 2, title: 'Reply to investor emails', type: 'Admin', estimated: 30, actual: 32 },
  { id: 3, title: 'Team sync', type: 'Meeting', estimated: 30, actual: 55 },
  { id: 4, title: 'Dentist appointment', type: 'Errand', estimated: 60, actual: 60 },
];

export const defaultVision =
  'I plan every day to build a calm, focused life: meaningful work, enough rest, and time for the people I love.';
