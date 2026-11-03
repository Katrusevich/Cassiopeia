// Дати працюють з ISO-рядками YYYY-MM-DD у локальній часовій зоні.
export const toISO = (d) => d.toLocaleDateString('en-CA');
export const fromISO = (iso) => new Date(`${iso}T00:00:00`);
export const todayISO = () => toISO(new Date());
export const addDays = (iso, n) => {
  const d = fromISO(iso);
  d.setDate(d.getDate() + n);
  return toISO(d);
};
export const fmt = (iso, opts) => fromISO(iso).toLocaleDateString('en-GB', opts);
