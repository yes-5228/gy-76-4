import { useState } from "react";
import { api } from "../api/client";
import { EmptyState } from "../components/EmptyState";

const initialForm = {
  student_id: "",
  teacher_id: "",
  course_name: "",
  hours: 1,
  checked_at: new Date().toISOString().slice(0, 10),
  note: "",
};

export function AttendancePage({ students, teachers, attendance, onCreated }) {
  const [form, setForm] = useState(initialForm);
  const [message, setMessage] = useState("");

  const submit = async (event) => {
    event.preventDefault();
    setMessage("");
    try {
      await api.checkIn(form);
      setForm(initialForm);
      await onCreated();
      setMessage("签到成功，课时已扣减");
    } catch (error) {
      setMessage(error.message);
    }
  };

  const onStudentChange = (studentId) => {
    const student = students.find((item) => item.id === studentId);
    setForm((current) => ({
      ...current,
      student_id: studentId,
      course_name: student?.course || current.course_name,
    }));
  };

  return (
    <div className="two-column">
      <section className="panel">
        <div className="panel-heading">
          <h2>签到打卡</h2>
          <span>自动扣减课时</span>
        </div>
        <form className="form-stack" onSubmit={submit}>
          <label>
            学员
            <select value={form.student_id} onChange={(event) => onStudentChange(event.target.value)} required>
              <option value="">请选择学员</option>
              {students.map((student) => (
                <option key={student.id} value={student.id}>
                  {student.name}（余 {student.remaining_hours}）
                </option>
              ))}
            </select>
          </label>
          <label>
            授课教师
            <select value={form.teacher_id} onChange={(event) => setForm({ ...form, teacher_id: event.target.value })} required>
              <option value="">请选择教师</option>
              {teachers.map((teacher) => (
                <option key={teacher.id} value={teacher.id}>
                  {teacher.name} / {teacher.subject}
                </option>
              ))}
            </select>
          </label>
          <div className="form-row">
            <label>
              课程
              <input value={form.course_name} onChange={(event) => setForm({ ...form, course_name: event.target.value })} required />
            </label>
            <label>
              课时
              <input
                type="number"
                min="0.5"
                step="0.5"
                value={form.hours}
                onChange={(event) => setForm({ ...form, hours: Number(event.target.value) })}
                required
              />
            </label>
          </div>
          <label>
            日期
            <input type="date" value={form.checked_at} onChange={(event) => setForm({ ...form, checked_at: event.target.value })} />
          </label>
          <label>
            备注
            <textarea value={form.note} onChange={(event) => setForm({ ...form, note: event.target.value })} rows="3" />
          </label>
          <button className="primary-button" type="submit">确认签到</button>
          {message ? <div className="inline-message">{message}</div> : null}
        </form>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>签到记录</h2>
          <span>{attendance.length} 条</span>
        </div>
        {attendance.length ? (
          attendance.map((record) => (
            <div className="table-row" key={record.id}>
              <div>
                <strong>{record.student_name}</strong>
                <span>{record.checked_at} / {record.teacher_name} / {record.course_name}</span>
              </div>
              <b>{record.hours} 课时</b>
            </div>
          ))
        ) : (
          <EmptyState text="暂无签到记录" />
        )}
      </section>
    </div>
  );
}
