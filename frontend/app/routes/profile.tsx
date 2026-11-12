import { useEffect, useState } from "react";
import { getMe, updateMe, type User } from "../lib/api";

export function meta() {
  return [
    { title: "Мой профиль — Self Market" },
    { name: "description", content: "Профиль участника Self Market." },
  ];
}

export default function ProfilePage() {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState("");
  const [name, setName] = useState("");
  const [city, setCity] = useState("");
  const [description, setDescription] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const savedToken = window.localStorage.getItem("self-market-token") || "";
    setToken(savedToken);
    if (!savedToken) {
      setMessage("Сначала войдите в аккаунт.");
      return;
    }
    getMe(savedToken).then((profile) => {
      setUser(profile);
      setName(profile.name);
      setCity(profile.city);
      setDescription(profile.description ?? "");
    }).catch((error) => setMessage(error instanceof Error ? error.message : "Не удалось загрузить профиль"));
  }, []);

  async function handleSave(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      const updated = await updateMe({ name: name.trim(), city: city.trim(), description: description.trim() }, token);
      setUser(updated);
      setMessage("Изменения сохранены.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Не удалось сохранить изменения");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">self<span>.</span>market</a>
        <nav className="main-nav">
          <a href="/">Заказы</a>
          <a href="/services">Услуги</a>
          <a className="active" href="/profile">Профиль</a>
        </nav>
        <a className="text-button" href="/">На главную</a>
      </header>

      <section className="page-intro">
        <p className="eyebrow">ЛИЧНЫЙ КАБИНЕТ</p>
        <h1>Мой профиль</h1>
        <p className="muted">Информация о вас и ваша активность в сообществе.</p>
      </section>

      {!user ? (
        <p className="notice">{message || "Загружаем профиль…"}</p>
      ) : (
        <section className="profile-layout">
          <aside className="profile-summary">
            <div className="avatar-placeholder">{user.name.trim().charAt(0).toUpperCase()}</div>
            <h2>{user.name}</h2>
            <p className="muted">{user.city}</p>
            <div className="profile-stats">
              <div><strong>{(user.balance_minutes / 60).toFixed(1)}</strong><span>часов на балансе</span></div>
              <div><strong>{user.rating_average.toFixed(1)}</strong><span>средний рейтинг</span></div>
              <div><strong>{user.reviews_count}</strong><span>отзывов</span></div>
              <div><strong>{user.total_hours_worked}</strong><span>часов получено</span></div>
            </div>
          </aside>

          <section className="profile-edit-card">
            <p className="eyebrow">ВАШИ ДАННЫЕ</p>
            <h2>Редактировать профиль</h2>
            <p className="muted">Номер телефона используется для входа и здесь не редактируется.</p>
            <div className="profile-phone"><span>Номер телефона</span><strong>{user.phone_number}</strong></div>
            <form className="auth-form" onSubmit={handleSave}>
              <label>Имя<input value={name} onChange={(event) => setName(event.target.value)} required /></label>
              <label>Город<input value={city} onChange={(event) => setCity(event.target.value)} required /></label>
              <label>О себе<textarea value={description} onChange={(event) => setDescription(event.target.value)} rows={5} placeholder="Расскажите немного о себе" /></label>
              {message && <p className="form-message">{message}</p>}
              <button className="primary-button" disabled={busy}>{busy ? "Сохраняем…" : "Сохранить изменения"}</button>
            </form>
          </section>
        </section>
      )}
    </main>
  );
}
