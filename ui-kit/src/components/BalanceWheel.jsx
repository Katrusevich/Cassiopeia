/** Радар-діаграма «Колесо балансу». data: [{ label, value }], value 0–max (у продукті max = 9). */
export function BalanceWheel({ data, max = 9 }) {
  const cx0 = 195;
  const cy0 = 140;
  const R = 90;
  const n = data.length;
  const angle = (i) => (-90 + (360 / n) * i) * (Math.PI / 180);
  const point = (i, r) => [cx0 + r * Math.cos(angle(i)), cy0 + r * Math.sin(angle(i))];
  const ring = (f) => data.map((_, i) => point(i, R * f).join(',')).join(' ');
  const area = data.map((d, i) => point(i, (R * d.value) / max).join(',')).join(' ');
  return (
    <svg className="cs-wheel" viewBox="0 0 390 280" role="img" aria-label="Wheel of balance">
      {[0.25, 0.5, 0.75, 1].map((f) => (
        <polygon key={f} className="cs-wheel__grid" points={ring(f)} />
      ))}
      {data.map((d, i) => {
        const [x, y] = point(i, R);
        return <line key={d.label} className="cs-wheel__axis" x1={cx0} y1={cy0} x2={x} y2={y} />;
      })}
      <polygon className="cs-wheel__area" points={area} />
      {data.map((d, i) => {
        const [x, y] = point(i, (R * d.value) / max);
        const [lx, ly] = point(i, R + 12);
        const side = Math.cos(angle(i));
        // Підписи праворуч і ліворуч вирівнюємо від кола, щоб довгі назви не перекривали діаграму.
        const anchor = side > 0.3 ? 'start' : side < -0.3 ? 'end' : 'middle';
        const dy = Math.sin(angle(i)) < -0.9 ? -6 : Math.sin(angle(i)) > 0.9 ? 8 : 0;
        return (
          <g key={d.label}>
            <circle className="cs-wheel__dot" cx={x} cy={y} r="4" />
            <text className="cs-wheel__label" x={lx} y={ly + dy} textAnchor={anchor} dominantBaseline="middle">
              {d.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
