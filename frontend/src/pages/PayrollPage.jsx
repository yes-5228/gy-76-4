import { useEffect, useState } from "react";
import { api } from "../api/client";
import { currency, currentMonth } from "../utils/format";

export function PayrollPage({ onSettled }) {
  const [month, setMonth] = useState(currentMonth());
  const [rows, setRows] = useState([]);
  const [message, setMessage] = useState("");

  const load = async () => {
    const data = await api.payroll(month);
    setRows(data);
  };

  useEffect(() => {
    load().catch((error) => setMessage(error.message));
  }, [month]);

  const settle = async (teacherId) => {
    setMessage("");
    try {
      await api.settlePayroll({ teacher_id: teacherId, month });
      await load();
      await onSettled();
      setMessage("已标记结算");
    } catch (error) {
      setMessage(error.message);
    }
  };

  return (
    <section className="panel wide-panel">
      <div className="panel-heading">
        <h2>教师课酬</h2>
        <label className="month-picker">
          月份
          <input type="month" value={month} onChange={(event) => setMonth(event.target.value)} />
        </label>
      </div>
      <div className="payroll-table">
        <div className="payroll-head">
          <span>教师</span>
          <span>科目</span>
          <span>课时</span>
          <span>课时费</span>
          <span>应发</span>
          <span>状态</span>
        </div>
        {rows.map((row) => (
          <div className="payroll-row" key={row.teacher_id}>
            <strong>{row.teacher_name}</strong>
            <span>{row.subject}</span>
            <span>{row.total_hours}</span>
            <span>{currency(row.hourly_rate)}</span>
            <b>{currency(row.amount)}</b>
            {row.status === "settled" ? (
              <span className="status-pill">已结算</span>
            ) : (
              <button className="small-button" type="button" onClick={() => settle(row.teacher_id)}>
                标记结算
              </button>
            )}
          </div>
        ))}
      </div>
      {message ? <div className="inline-message">{message}</div> : null}
    </section>
  );
}
