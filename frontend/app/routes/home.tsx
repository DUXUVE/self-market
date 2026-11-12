import { useEffect, useState } from "react";
import { applyToOrder, getCategories, getMe, getOrders, login, register, type Category, type Order, type User } from "../lib/api";

type AuthMode = "login" | "register";

export function meta() {
  return [
    { title: "Self Market — обмен временем" },
    { name: "description", content: "Помогайте друг другу и обменивайтесь временем." },
  ];
}

export default function Home() {
  const [token, setToken] = useState("");
  const [user, setUser] = useState<User | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [mode, setMode] = useState<AuthMode>("login");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [city, setCity] = useState("");
  const [filterCity, setFilterCity] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);

  async function loadMarketplace(currentToken: string) {
    const [profile, orderList, categoryList] = await Promise.all([
      getMe(currentToken), getOrders(), getCategories(),
    ]);
    setUser(profile);
    setOrders(orderList);
    setCategories(categoryList);
  }

  useEffect(() => {
    const savedToken = window.localStorage.getItem("self-market-token");
    if (!savedToken) {
      getCategories().then(setCategories).catch(() => undefined).finally(() => setLoading(false));
      return;
    }
    setToken(savedToken);
    loadMarketplace(savedToken).catch(() => {
      window.localStorage.removeItem("self-market-token");
      setToken("");
    }).finally(() => setLoading(false));
  }, []);

  async function handleAuth(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      if (mode === "register") await register({ phone_number: phone, password, name, city });
      const result = await login(phone, password);
      window.localStorage.setItem("self-market-token", result.access_token);
      setToken(result.access_token);
      await loadMarketplace(result.access_token);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Что-то пошло не так");
    } finally { setBusy(false); }
  }

  async function handleSearch(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try { setOrders(await getOrders(filterCity, categoryId)); }
    catch (error) { setMessage(error instanceof Error ? error.message : "Не удалось загрузить заказы"); }
    finally { setBusy(false); }
  }

  async function handleApply(orderId: number) {
    setMessage("");
    try {
      await applyToOrder(orderId, token);
      setMessage("Отклик отправлен!");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Не удалось отправить отклик");
    }
  }

  function logout() {
    window.localStorage.removeItem("self-market-token");
    setToken(""); setUser(null); setMode("login");
  }

  if (loading) return <main className="loading-screen">Загружаем Self Market…</main>;

  if (!token || !user) {
    return (
      <main className="auth-layout">
        <section className="auth-intro">
          <a className="brand" href="/">self<span>.</span>market</a>
          <div>
            <p className="eyebrow">ОБМЕН ВРЕМЕНЕМ</p>
            <h1>Время — это<br />то, чем можно<br /><span>делиться.</span></h1>
            <p className="intro-copy">Находите помощь рядом, делитесь своими навыками и получайте время за время.</p>
          </div>
          <p className="intro-foot">Помогаем друг другу — вместе.</p>
        </section>
        <section className="auth-panel">
          <div className="auth-card">
            <p className="eyebrow">{mode === "login" ? "С ВОЗВРАЩЕНИЕМ" : "СОЗДАЙТЕ АККАУНТ"}</p>
            <h2>{mode === "login" ? "Войти" : "Регистрация"}</h2>
            <p className="muted">{mode === "login" ? "Рады снова видеть вас." : "Присоединяйтесь к сообществу Self Market."}</p>
            <form onSubmit={handleAuth} className="auth-form">
              {mode === "register" && <>
                <label>Как вас зовут<input value={name} onChange={(e) => setName(e.target.value)} placeholder="Ваше имя" required /></label>
                <label>Город<input value={city} onChange={(e) => setCity(e.target.value)} placeholder="Например, Казань" required /></label>
              </>}
              <label>Номер телефона<input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+7 900 000-00-00" autoComplete="tel" required /></label>
              <label>Пароль<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Ваш пароль" autoComplete={mode === "login" ? "current-password" : "new-password"} required /></label>
              {message && <p className="form-message">{message}</p>}
              <button className="primary-button" disabled={busy}>{busy ? "Подождите…" : mode === "login" ? "Войти в аккаунт" : "Создать аккаунт"}</button>
            </form>
            <p className="switch-auth">{mode === "login" ? "Ещё нет аккаунта?" : "Уже есть аккаунт?"}{" "}
              <button onClick={() => { setMode(mode === "login" ? "register" : "login"); setMessage(""); }}>
                {mode === "login" ? "Зарегистрироваться" : "Войти"}
              </button>
            </p>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">self<span>.</span>market</a>
        <nav className="main-nav"><a className="active" href="/">Заказы</a><a href="/services">Услуги</a></nav>
        <div className="user-menu">
          <span className="user-name">{user.name}</span>
          <span className="balance">{Math.floor(user.balance_minutes / 60)} ч {user.balance_minutes % 60} мин</span>
          <button className="text-button" onClick={logout}>Выйти</button>
        </div>
      </header>
      <section className="welcome-block">
        <div><p className="eyebrow">МАРКЕТПЛЕЙС ВРЕМЕНИ</p><h1>Привет, {user.name.split(" ")[0]}.</h1>
          <p className="muted">Найдите помощь или поделитесь тем, что умеете.</p></div>
        <div className="balance-card"><span>Ваш баланс</span><strong>{(user.balance_minutes / 60).toFixed(1)} <small>часа</small></strong></div>
      </section>
      <section className="market-section">
        <div className="section-heading"><div><p className="eyebrow">СООБЩЕСТВО</p><h2>Открытые заказы</h2></div><span className="count">{orders.length} объявлений</span></div>
        <form className="filters" onSubmit={handleSearch}>
          <input value={filterCity} onChange={(e) => setFilterCity(e.target.value)} placeholder="Город" />
          <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
            <option value="">Все категории</option>
            {categories.map((category) => <option key={category.id} value={category.id}>{category.title}</option>)}
          </select>
          <button className="primary-button search-button" disabled={busy}>Найти</button>
        </form>
        {message && <p className="notice">{message}</p>}
        {orders.length === 0 ? <div className="empty-state"><span>✳</span><h3>Пока здесь тихо</h3><p>Открытых заказов пока нет. Загляните позже или измените фильтры.</p></div> :
          <div className="order-grid">{orders.map((order) => <article className="order-card" key={order.id}>
            <div className="order-meta"><span>{categories.find((item) => item.id === order.category_id)?.title ?? "Другое"}</span><span>{order.city}</span></div>
            <h3>{order.title}</h3><p className="order-description">{order.description}</p>
            <div className="order-bottom"><strong>{order.price} ч <small>времени</small></strong><button onClick={() => handleApply(order.id)} disabled={order.user_id === user.id}>Откликнуться</button></div>
            {order.user_id === user.id && <span className="own-order">Ваш заказ</span>}
          </article>)}</div>}
      </section>
    </main>
  );
}
