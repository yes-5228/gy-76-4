import { useState } from "react";
import { api } from "../api/client";

const initialForm = {
  name: "",
  guardian: "",
  phone: "",
  course: "",
  remaining_hours: 12,
};

export function StudentsPage({ students, reminders, onCreated }) {
  const [form, setForm] = useState(initialForm);
  const [message, setMessage] = useState("");

  const submit = async (event) => {
    event.preventDefault();
    setMessage("");
    try {
      await api.createStudent(form);
      setForm(initialForm);
      await onCreated();
      setMessage("学员已新增");
    } catch (error) {
      setMessage(error.message);
    }
  };

  return (
    <div className="two-column">
      <section className="panel">
        <div className="panel-heading">
          <h2>新增学员</h2>
          <span>建档后可直接签到</span>
        </div>
        <form className="form-stack" onSubmit={submit}>
          <div className="form-row">
            <label>
              姓名
              <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required />
            </label>
            <label>
              课程
              <input value={form.course} onChange={(event) => setForm({ ...form, course: event.target.value })} required />
            </label>
          </div>
          <div className="form-row">
            <label>
              家长
              <input value={form.guardian} onChange={(event) => setForm({ ...form, guardian: event.target.value })} required />
            </label>
            <label>
              电话
              <input value={form.phone} onChange={(event) => setForm({ ...form, phone: event.target.value })} required />
            </label>
          </div>
          <label>
            初始课时
            <input
              type="number"
              min="0"
              step="0.5"
              value={form.remaining_hours}
              onChange={(event) => setForm({ ...form, remaining_hours: Number(event.target.value) })}
            />
          </label>
          <button className="primary-button" type="submit">保存学员</button>
          {message ? <div className="inline-message">{message}</div> : null}
        </form>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>学员课时</h2>
          <span>{students.length} 人</span>
        </div>
        {students.map((student) => {
          const warning = reminders.some((item) => item.id === student.id);
          return (
            <div className="table-row" key={student.id}>
              <div>
                <strong>{student.name}</strong>
                <span>{student.course} / {student.guardian} / {student.phone}</span>
              </div>
              <b className={warning ? "warning-text" : ""}>{student.remaining_hours} 课时</b>
            </div>
          );
        })}
      </section>
    </div>
  );
}
