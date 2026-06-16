export function currency(value) {
  return new Intl.NumberFormat("zh-CN", {
    style: "currency",
    currency: "CNY",
    maximumFractionDigits: 0,
  }).format(value || 0);
}

export function currentMonth() {
  return new Date().toISOString().slice(0, 7);
}
