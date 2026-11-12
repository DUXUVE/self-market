import { useEffect, useState } from "react";
import { getMe, getWalletOperations, type User, type WalletOperation } from "../lib/api";

export function meta() {
  return [{ title: "Баланс и операции — Self Market" }];
}

function formatBalance(minutes: number) {
  const hours = Math.floor(minutes / 60);
  const rest = minutes % 60;
  return rest ? `${hours} ч ${rest} мин` : `${hours} ч`;
}

function operationStatus(status: string) {
  if (status === "completed") return "Завершено";
  if (status === "frozen") return "Минуты заморожены";
  if (status === "awaiting_confirmation") return "Ожидает подтверждения";
  return status;
}

export default function WalletPage() {
  const [user, setUser] = useState<User | null>(null);
  const [operations, setOperations] = useState<WalletOperation[]>([]);
  const [message, setMessage] = useState("Загружаем баланс и историю…");

  useEffect(() => {
    const token = window.localStorage.getItem("self-market-token") || "";
    if (!token) {
      setMessage("Чтобы посмотреть баланс и операции, войдите в аккаунт.");
      return;
    }

    Promise.all([getMe(token), getWalletOperations(token)])
      .then(([profile, history]) => {
        setUser(profile);
        setOperations(history);
        setMessage(history.length ? "" : "Операций пока нет. Здесь появится история обмена временем.");
      })
      .catch((error) => setMessage(error instanceof Error ? error.message : "Не удалось загрузить историю операций"));
  }, []);

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">self<span>.</span>market</a>
        <nav className="main-nav">
          <a href="/">Заказы</a>
          <a href="/services">Услуги</a>
          <a href="/chats">Сообщения</a>
          <a href="/profile">Профиль</a>
        </nav>
        <a className="text-button" href="/profile">В профиль</a>
      </header>

      <section className="page-intro">
        <p className="eyebrow">ВАШИ ЧАСЫ</p>
        <h1>Баланс и операции</h1>
        <p className="muted">Следите за начислениями и списаниями времени.</p>
      </section>

      {user && (
        <section className="wallet-summary">
          <span>Доступно на балансе</span>
          <strong>{formatBalance(user.balance_minutes)}</strong>
          <small>Время в Self Market</small>
        </section>
      )}

      <section className="wallet-history">
        <div className="section-heading">
          <div><p className="eyebrow">ИСТОРИЯ</p><h2>Последние операции</h2></div>
          <span className="count">{operations.length} операций</span>
        </div>

        {message && <p className={user ? "muted" : "notice"}>{message}</p>}

        {operations.length > 0 && (
          <div className="operation-list">
            {operations.map((operation) => {
              const isIncoming = user?.id === operation.user_id;
              return (
                <article className="operation-item" key={operation.id}>
                  <div className="operation-main">
                    <strong>{operation.order_title}</strong>
                    <span>{isIncoming ? `От: ${operation.sender_name}` : `Кому: ${operation.receiver_name}`}</span>
                    <small>{new Date(operation.created_at).toLocaleString("ru-RU")}</small>
                  </div>
                  <div className="operation-value">
                    <strong>{isIncoming ? "+" : "−"}{operation.hours_amount} ч</strong>
                    <span>{operationStatus(operation.status)}</span>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>
    </main>
  );
}
