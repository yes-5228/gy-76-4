import { useEffect, useState } from "react";
import { api } from "../api/client";
import { currency, currentMonth } from "../utils/format";

export function PayrollPage({ onSettled }) {
  const [month, setMonth] = useState(currentMonth());
  const [rows, setRows] = useState([]);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("info");
  const [expandedTeacher, setExpandedTeacher] = useState(null);

  const load = async () => {
    const data = await api.payroll(month);
    setRows(data);
  };

  useEffect(() => {
    load().catch((error) => setMessage(error.message));
  }, [month]);

  const settle = async (teacherId, teacherName) => {
    setMessage("");
    setMessageType("info");
    try {
      await api.settlePayroll({ teacher_id: teacherId, month });
      await load();
      await onSettled();
      setMessage(`${teacherName} ${month} 月已标记结算，当月课时记录已锁定`);
    } catch (error) {
      setMessage(error.message);
      setMessageType("error");
    }
  };

  const revoke = async (teacherId, teacherName, adjustmentCount) => {
    const confirmText = adjustmentCount > 0
      ? `确认撤回 ${teacherName} ${month} 月的结算吗？\n\n撤回后该月将恢复为未结算状态，且当前已有的 ${adjustmentCount} 条差额调整记录会被全部清除。`
      : `确认撤回 ${teacherName} ${month} 月的结算吗？\n\n撤回后该月将恢复为未结算状态。`;
    if (!confirm(confirmText)) {
      return;
    }
    setMessage("");
    setMessageType("info");
    try {
      await api.revokeSettlement({ teacher_id: teacherId, month });
      await load();
      await onSettled();
      setMessage(`已撤回 ${teacherName} ${month} 月的结算${adjustmentCount > 0 ? `，${adjustmentCount} 条差额调整已清除` : ""}`);
      setMessageType("warning");
    } catch (error) {
      setMessage(error.message);
      setMessageType("error");
    }
  };

  const toggleExpand = (teacherId) => {
    setExpandedTeacher(expandedTeacher === teacherId ? null : teacherId);
  };

  const messageClass =
    messageType === "error"
      ? "inline-message error"
      : messageType === "warning"
      ? "inline-message warning"
      : "inline-message";

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
          <span>结算课时</span>
          <span>调整课时</span>
          <span>课时费</span>
          <span>结算金额</span>
          <span>差额调整</span>
          <span>实发金额</span>
          <span>操作</span>
        </div>
        {rows.map((row) => (
          <div key={row.teacher_id}>
            <div className={`payroll-row ${row.is_locked ? "locked" : ""}`}>
              <strong>{row.teacher_name}</strong>
              <span>{row.subject}</span>
              <span>
                {row.is_locked ? row.settled_hours : row.current_hours}
                {row.is_locked && row.current_hours !== row.settled_hours + row.adjustment_hours && (
                  <span className="diff-indicator" title="当前课时与结算+调整有差异">
                    {" "}
                    (现:{row.current_hours})
                  </span>
                )}
              </span>
              <span className={row.adjustment_hours !== 0 ? "adjust-value" : ""}>
                {row.adjustment_hours > 0 ? `+${row.adjustment_hours}` : row.adjustment_hours}
              </span>
              <span>{currency(row.hourly_rate)}</span>
              <span className="settled-amount">
                {row.is_locked ? currency(row.settled_amount) : "-"}
              </span>
              <span
                className={
                  row.adjustment_amount > 0
                    ? "adjust-value positive"
                    : row.adjustment_amount < 0
                    ? "adjust-value negative"
                    : ""
                }
              >
                {row.adjustment_amount > 0
                  ? `+${currency(row.adjustment_amount)}`
                  : row.adjustment_amount < 0
                  ? currency(row.adjustment_amount)
                  : "-"}
              </span>
              <b>{currency(row.amount)}</b>
              {row.status === "settled" ? (
                <div className="row-actions">
                  <span className="status-pill locked">已结算🔒</span>
                  <button
                    className="small-button danger outline"
                    type="button"
                    onClick={() => revoke(row.teacher_id, row.teacher_name, row.adjustments.length)}
                  >
                    撤回
                  </button>
                </div>
              ) : (
                <button
                  className="small-button"
                  type="button"
                  onClick={() => settle(row.teacher_id, row.teacher_name)}
                >
                  标记结算
                </button>
              )}
            </div>
            {row.is_locked && row.adjustments.length > 0 && (
              <div
                className={`adjustments-panel ${expandedTeacher === row.teacher_id ? "open" : ""}`}
              >
                <button
                  type="button"
                  className="adjustments-toggle"
                  onClick={() => toggleExpand(row.teacher_id)}
                >
                  {expandedTeacher === row.teacher_id ? "▼" : "▶"} 查看 {row.adjustments.length} 条差额调整明细
                </button>
                {expandedTeacher === row.teacher_id && (
                  <div className="adjustments-list">
                    {row.adjustments.map((adj) => (
                      <div className="adjustment-item" key={adj.id}>
                        <span className="adj-date">{adj.created_at}</span>
                        <span className="adj-reason">{adj.reason}</span>
                        <span
                          className={
                            adj.hours_diff > 0
                              ? "adj-hours positive"
                              : adj.hours_diff < 0
                              ? "adj-hours negative"
                              : ""
                          }
                        >
                          {adj.hours_diff > 0 ? `+${adj.hours_diff}` : adj.hours_diff}课时
                        </span>
                        <span
                          className={
                            adj.amount_diff > 0
                              ? "adj-amount positive"
                              : adj.amount_diff < 0
                              ? "adj-amount negative"
                              : ""
                          }
                        >
                          {adj.amount_diff > 0
                            ? `+${currency(adj.amount_diff)}`
                            : currency(adj.amount_diff)}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
      {message ? <div className={messageClass}>{message}</div> : null}
      <div className="payroll-footnote">
        <p>
          <strong>说明：</strong>
          标记结算后，该月课时记录将被锁定。后续在已结算月份新增或撤销签到时，
          将自动生成「差额调整」记录，原始结算金额保持不变。
          撤回结算会清除该月所有差额调整记录。
        </p>
      </div>
    </section>
  );
}
