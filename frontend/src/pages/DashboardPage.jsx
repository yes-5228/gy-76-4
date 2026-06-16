import { EmptyState } from "../components/EmptyState";
import { StatCard } from "../components/StatCard";
import { currency } from "../utils/format";

export function DashboardPage({ data }) {
  const dashboard = data.dashboard || {};

  return (
    <div className="page-grid">
      <div className="stats-grid">
        <StatCard label="在读学员" value={dashboard.active_students || 0} />
        <StatCard label="续费提醒" value={dashboard.renewal_count || 0} tone="warning" />
        <StatCard label="本月课消" value={`${dashboard.month_consumed_hours || 0} 课时`} tone="success" />
        <StatCard label="本月课酬" value={currency(dashboard.month_payroll_amount)} />
      </div>

      <section className="panel">
        <div className="panel-heading">
          <h2>续费跟进</h2>
          <span>{data.reminders.length} 位学员</span>
        </div>
        {data.reminders.length ? (
          <div className="table-list">
            {data.reminders.map((student) => (
              <div className="table-row" key={student.id}>
                <div>
                  <strong>{student.name}</strong>
                  <span>{student.course} / {student.guardian}</span>
                </div>
                <b>{student.remaining_hours} 课时</b>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState text="暂无需要续费提醒的学员" />
        )}
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>最近签到</h2>
          <span>{data.attendance.length} 条记录</span>
        </div>
        {data.attendance.slice(0, 6).map((record) => (
          <div className="table-row" key={record.id}>
            <div>
              <strong>{record.student_name}</strong>
              <span>{record.course_name} / {record.teacher_name}</span>
            </div>
            <b>{record.hours} 课时</b>
          </div>
        ))}
      </section>
    </div>
  );
}
