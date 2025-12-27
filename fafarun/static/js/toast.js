document.body.addEventListener("toast", (e) => {
  const root = document.querySelector("#toast-root");
  if (!root) return;

  const t = document.createElement("div");
  const type = e.detail?.type || "info";

  t.className = "toast toast--" + type;
  t.textContent = e.detail?.message || "OK";

  root.prepend(t);
  setTimeout(() => t.remove(), e.detail?.timeout ?? 3000);
});
