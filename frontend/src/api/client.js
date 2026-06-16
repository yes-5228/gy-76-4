const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(data?.message || "请求失败");
  }
  return data;
}

export const api = {
  dashboard: () => request("/dashboard"),
  students: () => request("/students"),
  createStudent: (payload) => request("/students", { method: "POST", body: JSON.stringify(payload) }),
  teachers: () => request("/teachers"),
  attendance: () => request("/attendance"),
  checkIn: (payload) => request("/attendance", { method: "POST", body: JSON.stringify(payload) }),
  reminders: () => request("/reminders"),
  payroll: (month) => request(`/payroll?month=${month}`),
  settlePayroll: (payload) => request("/payroll/settle", { method: "POST", body: JSON.stringify(payload) }),
};
