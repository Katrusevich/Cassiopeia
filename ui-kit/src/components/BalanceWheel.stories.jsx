import { BalanceWheel } from './BalanceWheel.jsx';

export default { title: 'Components/BalanceWheel', component: BalanceWheel };

export const Default = {
  args: {
    data: [
      { label: 'Career', value: 8 },
      { label: 'Health', value: 4 },
      { label: 'Finance', value: 6 },
      { label: 'Family', value: 7 },
      { label: 'Growth', value: 5 },
      { label: 'Rest', value: 3 },
    ],
  },
};
