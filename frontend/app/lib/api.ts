const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1";

export type User = {
  id: number;
  phone_number: string;
  name: string;
  city: string;
  avatar_link: string | null;
  description: string | null;
  balance_minutes: number;
  rating_average: number;
  reviews_count: number;
  total_hours_worked: number;
};

export type Category = { id: number; title: string };

export type Order = {
  id: number;
  type: boolean;
  category_id: number;
  title: string;
  description: string;
  price: number;
  city: string;
  user_id: number;
  contractor_id: number | null;
  desired_date: string | null;
  creation_date: string;
};

export type Service = {
  id: number;
  user_id: number;
  category_id: number;
  title: string;
  description: string;
  price: number;
};

async function request<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body && !(options.body instanceof URLSearchParams)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!response.ok) {
    let message = "Не удалось выполнить запрос";
    try {
      const data = await response.json();
      message = typeof data.detail === "string" ? data.detail : message;
    } catch {
      // Ответ сервера может быть не в формате JSON.
    }
    throw new Error(message);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export function register(data: {
  phone_number: string;
  password: string;
  name: string;
  city: string;
}) {
  return request<User>("/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function login(phone: string, password: string) {
  const body = new URLSearchParams({ username: phone, password });
  return request<{ access_token: string; token_type: string }>("/auth/login", {
    method: "POST",
    body,
  });
}

export function getMe(token: string) {
  return request<User>("/users/me", {}, token);
}

export function getCategories() {
  return request<Category[]>("/categories");
}

export function getOrders(city = "", categoryId = "") {
  const params = new URLSearchParams({ open_only: "true" });
  if (city.trim()) params.set("city", city.trim());
  if (categoryId) params.set("category_id", categoryId);
  return request<Order[]>(`/orders?${params.toString()}`);
}

export function applyToOrder(orderId: number, token: string) {
  return request(`/orders/${orderId}/apply`, { method: "POST" }, token);
}

export function getServices(categoryId = "") {
  const params = new URLSearchParams();
  if (categoryId) params.set("category_id", categoryId);
  const query = params.toString();
  return request<Service[]>(`/services${query ? `?${query}` : ""}`);
}

export function createService(
  data: { category_id: number; title: string; description: string; price: number },
  token: string,
) {
  return request<Service>("/services", {
    method: "POST",
    body: JSON.stringify(data),
  }, token);
}

export function updateMe(
  data: { name: string; city: string; description: string },
  token: string,
) {
  return request<User>("/users/me", {
    method: "PATCH",
    body: JSON.stringify(data),
  }, token);
}
