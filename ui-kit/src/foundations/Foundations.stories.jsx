import { useEffect, useRef, useState } from 'react';

export default { title: 'Foundations', parameters: { layout: 'padded' } };

const groups = {
  Primary: ['--color-primary', '--color-primary-hover', '--color-primary-active', '--color-on-primary'],
  Secondary: ['--color-secondary', '--color-secondary-hover', '--color-secondary-active', '--color-on-secondary'],
  Accent: ['--color-accent', '--color-accent-strong', '--color-accent-soft'],
  Neutral: [
    '--color-bg',
    '--color-surface',
    '--color-surface-raised',
    '--color-surface-alt',
    '--color-border',
    '--color-border-strong',
    '--color-text',
    '--color-text-muted',
    '--color-disabled-bg',
    '--color-disabled-fg',
  ],
  'Semantic · success / error / warning': [
    '--color-success',
    '--color-success-bg',
    '--color-error',
    '--color-error-bg',
    '--color-warning',
    '--color-warning-bg',
  ],
};

function Swatch({ token }) {
  const ref = useRef(null);
  const [value, setValue] = useState('');
  useEffect(() => {
    const read = () => {
      const el = ref.current;
      if (!el) return;
      // Беремо реальне значення, тож підпис оновлюється разом із темою.
      const probe = getComputedStyle(el).backgroundColor;
      const m = probe.match(/\d+(\.\d+)?/g)?.map(Number) || [];
      const hex = m.length >= 3 ? '#' + m.slice(0, 3).map((n) => Math.round(n).toString(16).padStart(2, '0')).join('') : probe;
      setValue(hex.toUpperCase());
    };
    read();
    const mo = new MutationObserver(read);
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    return () => mo.disconnect();
  }, []);
  return (
    <div style={{ width: 150, border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', overflow: 'hidden', background: 'var(--color-surface)' }}>
      <div ref={ref} style={{ height: 56, background: `var(${token})` }} />
      <div style={{ padding: 'var(--space-2)' }}>
        <div className="t-caption" style={{ color: 'var(--color-text)', fontWeight: 700 }}>{token.replace('--color-', '')}</div>
        <div className="t-caption">{value}</div>
      </div>
    </div>
  );
}

/** Палітра: primary / secondary / neutral / semantic. Перемикайте тему в тулбарі. */
export const Colors = {
  render: () => (
    <div style={{ display: 'grid', gap: 'var(--space-5)' }}>
      {Object.entries(groups).map(([name, tokens]) => (
        <section key={name}>
          <h3 className="t-h3" style={{ marginBottom: 'var(--space-3)' }}>{name}</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
            {tokens.map((t) => <Swatch key={t} token={t} />)}
          </div>
        </section>
      ))}
    </div>
  ),
};

const scale = [
  ['H1 · Playfair Display Bold', 't-h1', '--fs-h1'],
  ['H2 · Playfair Display Bold', 't-h2', '--fs-h2'],
  ['H3 · Playfair Display Medium', 't-h3', '--fs-h3'],
  ['Body · Lato Regular', 't-body', '--fs-body'],
  ['Small · Lato Regular', 't-small', '--fs-small'],
  ['Caption · Lato Regular', 't-caption', '--fs-caption'],
  ['Eyebrow · Lato Bold, uppercase', 't-eyebrow', '--fs-caption'],
];

/** Типографічна шкала: H1–H3, body, small, caption. */
export const Typography = {
  render: () => (
    <div style={{ display: 'grid', gap: 'var(--space-4)', maxWidth: 640 }}>
      {scale.map(([label, cls, token]) => (
        <div key={cls} style={{ display: 'grid', gridTemplateColumns: '110px 1fr', alignItems: 'baseline', gap: 'var(--space-4)' }}>
          <span className="t-caption">{token}</span>
          <span className={cls}>{label}</span>
        </div>
      ))}
      <p className="t-body" style={{ marginTop: 'var(--space-4)' }}>
        Body text sample: Cassiopeia turns a chaotic list of thoughts into a realistic plan for the day.
      </p>
    </div>
  ),
};

/** Відступи (крок 4px), радіуси й тіні. */
export const SpacingAndShape = {
  render: () => (
    <div style={{ display: 'grid', gap: 'var(--space-6)' }}>
      <section>
        <h3 className="t-h3" style={{ marginBottom: 'var(--space-3)' }}>Spacing</h3>
        {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
          <div key={n} style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-2)' }}>
            <span className="t-caption" style={{ width: 70 }}>--space-{n}</span>
            <div style={{ height: 14, width: `var(--space-${n})`, background: 'var(--color-secondary)', borderRadius: 2 }} />
          </div>
        ))}
      </section>
      <section>
        <h3 className="t-h3" style={{ marginBottom: 'var(--space-3)' }}>Radius &amp; shadow</h3>
        <div style={{ display: 'flex', gap: 'var(--space-4)', flexWrap: 'wrap' }}>
          {['sm', 'md', 'lg', 'xl'].map((r) => (
            <div key={r} style={{ width: 96, height: 72, display: 'grid', placeItems: 'center', background: 'var(--color-surface)', border: '1px solid var(--color-border-strong)', borderRadius: `var(--radius-${r})` }}>
              <span className="t-caption">radius-{r}</span>
            </div>
          ))}
          {['sm', 'md'].map((s) => (
            <div key={s} style={{ width: 96, height: 72, display: 'grid', placeItems: 'center', background: 'var(--color-surface-raised)', borderRadius: 'var(--radius-md)', boxShadow: `var(--shadow-${s})` }}>
              <span className="t-caption">shadow-{s}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  ),
};
