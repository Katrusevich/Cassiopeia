import { WHEEL_MAX, wheelData } from '../data/mock.js';
import { BalanceWheel } from './BalanceWheel.jsx';

export default { title: 'Components/BalanceWheel', component: BalanceWheel };

/** Вісім сфер, шкала 1–9 — як у PRD. */
export const Default = { args: { data: wheelData, max: WHEEL_MAX } };
