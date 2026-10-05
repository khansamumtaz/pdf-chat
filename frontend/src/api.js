const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const getToken = () => localStorage.getItem("token");
export const setToken = (t) => localStorage.setItem("token", t);
export const clearToken = () => localStorage.removeItem("token");

function messageFrom(data, status) {
  const d = data && data.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) return d.map((e) => e.msg).join(". ");
  return `Request failed (status ${status}).`;
}

async function request(path, { method = "GET", body, form, auth = true } = {}) {
  const headers = {};
  if (auth && getToken()) headers.Authorization = `Bearer ${getToken()}`;
  let payload;
  if (form) {
    payload = form;
  } else if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }

  let res;
  try {
    res = await fetch(BASE + path, { method, headers, body: payload });
  } catch {
    throw new Error("Cannot reach the server. Check that the backend is running.");
  }

  let data = null;
  try {
    data = await res.json();
  } catch {
    data = null;
  }

  if (!res.ok) {
    if (auth && (res.status === 401 || res.status === 403)) {
      clearToken();
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
      throw new Error("Your session has expired. Please log in again.");
    }
    const err = new Error(messageFrom(data, res.status));
    err.status = res.status;
    throw err;
  }
  return data;
}

export const api = {
  signup: (b) => request("/auth/signup", { method: "POST", body: b, auth: false }),
  verifyEmail: (b) => request("/auth/verify-email", { method: "POST", body: b, auth: false }),
  resendOtp: (b) => request("/auth/resend-otp", { method: "POST", body: b, auth: false }),
  login: (b) => request("/auth/login", { method: "POST", body: b, auth: false }),
  forgotPassword: (b) => request("/auth/forgot-password", { method: "POST", body: b, auth: false }),
  resetPassword: (b) => request("/auth/reset-password", { method: "POST", body: b, auth: false }),

  logout: () => request("/auth/logout", { method: "POST" }),
  me: () => request("/users/me"),
  updateMe: (b) => request("/users/me", { method: "PUT", body: b }),
  changePassword: (b) => request("/users/change-password", { method: "POST", body: b }),

  listDocs: () => request("/documents"),
  uploadDoc: (file) => {
    const form = new FormData();
    form.append("file", file);
    return request("/documents/upload", { method: "POST", form });
  },
  deleteDoc: (id) => request(`/documents/${id}`, { method: "DELETE" }),

  ask: (document_id, question) =>
    request("/chat/ask", { method: "POST", body: { document_id, question } }),
  history: (id) => request(`/chat/history/${id}`),
};
