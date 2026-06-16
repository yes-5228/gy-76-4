export function StatCard({ label, value, tone = "default" }) {
  return (
    <section className={`stat-card ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </section>
  );
}
