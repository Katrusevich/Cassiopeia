/** items: [{ id, label, icon, disabled }]; нижня навігація продукту. */
export function NavBar({ items, activeId, onChange }) {
  return (
    <nav className="cs-nav" aria-label="Main">
      {items.map(({ id, label, icon: Icon, disabled }) => (
        <button
          key={id}
          type="button"
          className="cs-nav__item"
          aria-current={id === activeId ? 'page' : undefined}
          disabled={disabled}
          onClick={() => onChange?.(id)}
        >
          <Icon size={20} aria-hidden="true" />
          {label}
        </button>
      ))}
    </nav>
  );
}
