import { useEffect, useState } from "react";
import { createOrder, getCategories, getMe, type Category } from "../lib/api";

export function meta() {
  return [{ title: "Создать заказ — Self Market" }];
}

export default function CreateOrderPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [token, setToken] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [price, setPrice] = useState("1");
  const [city, setCity] = useState("");
  const [desiredDate, setDesiredDate] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const savedToken = window.localStorage.getItem("self-market-token") || "";
    setToken(savedToken);
    getCategories().then(setCategories).catch((error) => {
      setMessage(error instanceof Error ? error.message : "Не удалось загрузить категории");
    });
    if (savedToken) {
      getMe(savedToken).then((user) => setCity(user.city)).catch(() => undefined);
    }
  }, []);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      setMessage("Сначала войдите в аккаунт.");
      return;
    }
    setBusy(true);
    setMessage("");
    try {
      const order = await createOrder({
        type: true,
        category_id: Number(categoryId),
        title: title.trim(),
        description: description.trim(),
        price: Number(price),
        city: city.trim(),
        desired_date: desiredDate || null,
      }, token);
      window.location.href = `/orders/${order.id}`;
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Не удалось создать заказ");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">self<span>.</span>market</a>
        <nav className="main-nav"><a href="/">Заказы</a><a href="/services">Услуги</a><a href="/chats">Сообщения</a><a href="/profile">Профиль</a></nav>
        <a className="text-button" href="/">Назад</a>
      </header>
      <section className="page-intro">
        <p className="eyebrow">НОВОЕ ОБЪЯВЛЕНИЕ</p>
        <h1>Создать заказ</h1>
        <p className="muted">Опишите, какая помощь вам нужна, и укажите стоимость в часах.</p>
      </section>
      <section className="create-service-card" style={{ maxWidth: 650, marginBottom: 70 }}>
        {!token ? <p className="form-message">Чтобы создать заказ, войдите в аккаунт на главной странице.</p> : (
          <form className="auth-form" onSubmit={handleSubmit}>
            <label>Название<input className="form-input" value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Например, нужна помощь с переездом" maxLength={255} required /></label>
            <label>Описание<textarea className="form-textarea" value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Подробно расскажите, что нужно сделать" required /></label>
            <label>Категория<select className="form-select" value={categoryId} onChange={(event) => setCategoryId(event.target.value)} required>
              <option value="">Выберите категорию</option>
              {categories.map((category) => <option key={category.id} value={category.id}>{category.title}</option>)}
            </select></label>
            <label>Стоимость, часов<input className="form-input" type="number" min="1" step="1" value={price} onChange={(event) => setPrice(event.target.value)} required /></label>
            <label>Город<input className="form-input" value={city} onChange={(event) => setCity(event.target.value)} placeholder="Ваш город" required /></label>
            <label>Желаемая дата (необязательно)<input className="form-input" type="datetime-local" value={desiredDate} onChange={(event) => setDesiredDate(event.target.value)} /></label>
            {message && <p className="form-message">{message}</p>}
            <button className="primary-button" disabled={busy}>{busy ? "Создаём…" : "Опубликовать заказ"}</button>
          </form>
        )}
      </section>
    </main>
  );
}
