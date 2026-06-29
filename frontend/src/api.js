// Thin fetch wrapper. Attaches the JWT and surfaces backend error detail.
const BASE = import.meta.env.VITE_API_URL || "";

export function getToken() {
  return localStorage.getItem("answerspot_token");
}

export function setToken(token) {
  if (token) localStorage.setItem("answerspot_token", token);
  else localStorage.removeItem("answerspot_token");
}

async function request(method, path, body) {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  let data = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { detail: text };
    }
  }

  if (!res.ok) {
    const detail = data?.detail || `Request failed (${res.status})`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data;
}

export const api = {
  get: (p) => request("GET", p),
  post: (p, b) => request("POST", p, b),
  health: () => request("GET", "/api/health"),
};
