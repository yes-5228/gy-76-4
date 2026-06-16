import { CalendarCheck, GraduationCap, LayoutDashboard, ReceiptText, UserRoundCheck } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { api } from "./api/client";
import { Header } from "./components/Header";
import { Sidebar } from "./components/Sidebar";
import { AttendancePage } from "./pages/AttendancePage";
import { DashboardPage } from "./pages/DashboardPage";
import { PayrollPage } from "./pages/PayrollPage";
import { StudentsPage } from "./pages/StudentsPage";

const navItems = [
  { id: "dashboard", label: "运营看板", icon: LayoutDashboard },
  { id: "attendance", label: "签到打卡", icon: CalendarCheck },
  { id: "students", label: "学员课时", icon: GraduationCap },
  { id: "payroll", label: "课酬结算", icon: ReceiptText },
];

export function App() {
  const [activePage, setActivePage] = useState("dashboard");
  const [data, setData] = useState({
    dashboard: null,
    students: [],
    teachers: [],
    attendance: [],
    reminders: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const refresh = async () => {
    setError("");
    const [dashboard, students, teachers, attendance, reminders] = await Promise.all([
      api.dashboard(),
      api.students(),
      api.teachers(),
      api.attendance(),
      api.reminders(),
    ]);
    setData({ dashboard, students, teachers, attendance, reminders });
  };

  useEffect(() => {
    refresh()
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const activeMeta = useMemo(() => navItems.find((item) => item.id === activePage), [activePage]);

  return (
    <div className="app-shell">
      <Sidebar items={navItems} activePage={activePage} onNavigate={setActivePage} />
      <main className="main-area">
        <Header
          icon={activeMeta?.icon || UserRoundCheck}
          title={activeMeta?.label || "少儿培训考勤系统"}
          subtitle="学员课消、续费跟进和教师课酬统一管理"
        />
        {error ? <div className="alert">{error}</div> : null}
        {loading ? (
          <div className="loading">正在加载数据...</div>
        ) : (
          <>
            {activePage === "dashboard" && <DashboardPage data={data} />}
            {activePage === "attendance" && (
              <AttendancePage
                students={data.students}
                teachers={data.teachers}
                attendance={data.attendance}
                onCreated={refresh}
              />
            )}
            {activePage === "students" && (
              <StudentsPage students={data.students} reminders={data.reminders} onCreated={refresh} />
            )}
            {activePage === "payroll" && <PayrollPage onSettled={refresh} />}
          </>
        )}
      </main>
    </div>
  );
}
