import { useEffect, useState } from "react";
import { createService, getCategories, getServices, type Category, type Service } from "../lib/api";

export function meta() {
  return [
    { title: "Услуги — Self Market" },
    { name: "description", content: "Услуги участников Self Market." },
  ];
}

export default function ServicesPage() {
  const [services, setServices] = useState<Service[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [token, setToken] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("1");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function loadServices() {
    setServices(await getServices(categoryId));
  }

  useEffect(() => {
    const savedToken = window.localStorage.getItem("self-market-token") || "";
    setToken(savedToken);
    Promise.all([getCategories(), getServices()])
      .then(([categoryList, serviceList]) => {
        setCategories(categoryList);
        setServices(serviceList);
      })
      .catch((error) => setMessage(error instanceof Error ? error.message : "Не удалось загрузить услуги"));
  }, []);

  async function handleFilter(nextCategoryId: string) {
    setCategoryId(nextCategoryId);
    try {
      setServices(await getServices(nextCategoryId));
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Не удалось загрузить услуги");
    }
  }

  async function handleCreate(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      setMessage("Войдите в аккаунт, чтобы добавить услугу.");
      return;
    }
    setBusy(true);
    setMessage("");
    try {
      await createService({
        category_id: Number(categoryIdForCreate),
        title: title.trim(),
        description: description.trim(),
        price: Number(price),
      }, token);
      setTitle("");
      setDescription("");
      setPrice("1");
      setMessage("Услуга опубликована!");
      await loadServices();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Не удалось создать услугу");
    } finally {
      setBusy(false);
    }
  }

  const [categoryIdForCreate, setCategoryIdForCreate] = useState("");

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">self<span>.</span>market</a>
        <nav className="main-nav">
          <a href="/">Заказы</a>
          <a className="active" href="/services">Услуги</a>
          <a href="/chats">Сообщения</a>
          <a href="/profile">Профиль</a>
        </nav>
        <a className="text-button" href="/">На главную</a>
      </header>

      <section className="page-intro">
        <p className="eyebrow">СООБЩЕСТВО SELF MARKET</p>
        <h1>Услуги участников</h1>
        <p className="muted">Делитесь своими навыками и находите тех, кто может помочь.</p>
      </section>

      <section className="services-layout">
        <div className="services-list-section">
          <div className="section-heading">
            <div><p className="eyebrow">ЧТО УМЕЮТ УЧАСТНИКИ</p><h2>Каталог услуг</h2></div>
            <span className="count">{services.length} услуг</span>
          </div>
          <label className="filter-label">Категория
            <select value={categoryId} onChange={(event) => handleFilter(event.target.value)}>
              <option value="">Все категории</option>
              {categories.map((category) => <option key={category.id} value={category.id}>{category.title}</option>)}
            </select>
          </label>
          {services.length === 0 ? (
            <div className="empty-state"><span>✳</span><h3>Пока нет услуг</h3><p>Можно стать первым и рассказать, чем вы можете помочь.</p></div>
          ) : (
            <div className="order-grid">
              {services.map((service) => (
                <article className="order-card" key={service.id}>
                  <div className="order-meta"><span>{categories.find((item) => item.id === service.category_id)?.title ?? "Услуга"}</span><span>Участник #{service.user_id}</span></div>
                  <h3>{service.title}</h3>
                  <p className="order-description">{service.description}</p>
                  <div className="order-bottom"><strong>{service.price} ч <small>времени</small></strong></div>
                </article>
              ))}
            </div>
          )}
        </div>

        <aside className="create-service-card">
          <p className="eyebrow">ПОДЕЛИТЕСЬ УМЕНИЯМИ</p>
          <h2>Добавить услугу</h2>
          <p className="muted">Расскажите, какую помощь вы можете предложить другим.</p>
          <form className="auth-form" onSubmit={handleCreate}>
            <label>Название<input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Например, помогу с английским" required /></label>
            <label>Описание<textarea value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Кратко опишите, что вы предлагаете" rows={4} required /></label>
            <label>Категория<select value={categoryIdForCreate} onChange={(event) => setCategoryIdForCreate(event.target.value)} required>
              <option value="">Выберите категорию</option>
              {categories.map((category) => <option key={category.id} value={category.id}>{category.title}</option>)}
            </select></label>
            <label>Стоимость, часов<input type="number" min="1" step="1" value={price} onChange={(event) => setPrice(event.target.value)} required /></label>
            {message && <p className="form-message">{message}</p>}
            <button className="primary-button" disabled={busy}>{busy ? "Публикуем…" : "Опубликовать услугу"}</button>
          </form>
          {!token && <p className="muted small-note">Для публикации нужно войти в аккаунт.</p>}
        </aside>
      </section>
    </main>
  );
}
