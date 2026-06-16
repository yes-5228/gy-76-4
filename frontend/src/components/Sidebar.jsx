export function Sidebar({ items, activePage, onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark">培</span>
        <div>
          <strong>童程考勤</strong>
          <span>Training Ops</span>
        </div>
      </div>
      <nav className="nav-list">
        {items.map((item) => {
          const Icon = item.icon;
          return (
            <button
              type="button"
              key={item.id}
              className={activePage === item.id ? "nav-item active" : "nav-item"}
              onClick={() => onNavigate(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
