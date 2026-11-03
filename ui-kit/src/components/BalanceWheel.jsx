/** Радар-діаграма «Колесо балансу». data: [{ label, value }], value 0–max. */
export function BalanceWheel({ data, max = 10 }) {
  const cx0 = 150;
  const cy0 = 140;
  const R = 90;
  const n = data.length;
  const point = (i, r) => {
    const a = (-90 + (360 / n) * i) * (Math.PI / 180);
    return [cx0 + r * Math.cos(a), cy0 + r * Math.sin(a)];
  };
  const ring = (f) => data.map((_, i) => point(i, R * f).join(',')).join(' ');
  const area = data.map((d, i) => point(i, (R * d.value) / max).join(',')).join(' ');
  return (
    <svg className="cs-wheel" viewBox="0 0 300 280" role="img" aria-label="Wheel of balance">
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
        const [lx, ly] = point(i, R + 20);
        return (
          <g key={d.label}>
            <circle className="cs-wheel__dot" cx={x} cy={y} r="4" />
            <text className="cs-wheel__label" x={lx} y={ly} textAnchor="middle" dominantBaseline="middle">
              {d.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
