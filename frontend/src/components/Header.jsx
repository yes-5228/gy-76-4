export function Header({ icon: Icon, title, subtitle }) {
  return (
    <header className="page-header">
      <div className="page-title">
        <span className="title-icon">
          <Icon size={22} />
        </span>
        <div>
          <h1>{title}</h1>
          <p>{subtitle}</p>
        </div>
      </div>
    </header>
  );
}
