import { App } from './App.jsx';

export default {
  title: 'Screens',
  component: App,
  parameters: { layout: 'fullscreen' },
};

/** Повний клікабельний прототип: нижня навігація, чат → план → Today, перенесення з Undo. */
export const Prototype = { args: { initialScreen: 'today' } };

export const Today = { args: { initialScreen: 'today' } };
export const Chat = { args: { initialScreen: 'chat' } };
/** Середина сценарію: ШІ запропонував план, користувач перевіряє картку. */
export const ChatPlanProposal = { args: { initialScreen: 'chat', preset: 'plan' } };
export const Week ={ args: { initialScreen: 'week' } };
export const Month = { args: { initialScreen: 'month' } };
export const Year = { args: { initialScreen: 'year' } };
export const WheelOfBalance = { args: { initialScreen: 'wheel' } };
export const VisionAndMission = { args: { initialScreen: 'vision' } };
export const TaskTracker = { args: { initialScreen: 'tracker' } };

/** Мобільний вигляд (бонус): той самий код, вузький viewport. */
export const MobileToday = {
  args: { initialScreen: 'today' },
  globals: { viewport: { value: 'mobile1', isRotated: false } },
};
