import { useEffect, useState } from "react";
import { getChats, getMe, getOrder, type Chat, type Order, type User } from "../lib/api";

type ChatItem = { chat: Chat; order: Order };

export function meta() {
  return [{ title: "Сообщения — Self Market" }];
}

export default function ChatsPage() {
  const [items, setItems] = useState<ChatItem[]>([]);
  const [user, setUser] = useState<User | null>(null);
  const [message, setMessage] = useState("Загружаем сообщения…");

  useEffect(() => {
    const token = window.localStorage.getItem("self-market-token") || "";
    if (!token) {
      setMessage("Чтобы увидеть сообщения, войдите в аккаунт.");
      return;
    }
    Promise.all([getChats(token), getMe(token)]).then(async ([chats, profile]) => {
      setUser(profile);
      const rows = await Promise.all(chats.map(async (chat) => ({
        chat,
        order: await getOrder(chat.order_id),
      })));
      setItems(rows);
      setMessage(rows.length ? "" : "Пока нет активных переписок. Они появятся после отклика на заказ.");
    }).catch((error) => setMessage(error instanceof Error ? error.message : "Не удалось загрузить чаты"));
  }, []);

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">self<span>.</span>market</a>
        <nav className="main-nav"><a href="/">Заказы</a><a href="/services">Услуги</a><a className="active" href="/chats">Сообщения</a><a href="/profile">Профиль</a></nav>
        <a className="text-button" href="/">На главную</a>
      </header>
      <section className="page-intro">
        <p className="eyebrow">ОБЩЕНИЕ</p>
        <h1>Сообщения</h1>
        <p className="muted">Переписки по вашим заказам и откликам.</p>
      </section>
      <section className="chat-list">
        {message && <p className="notice">{message}</p>}
        {items.map(({ chat, order }) => (
          <a className="chat-list-item" href={`/chats/${chat.id}`} key={chat.id}>
            <div><span className="eyebrow">ЗАКАЗ #{order.id}</span><h2>{order.title}</h2><p className="muted">{order.city} · {order.price} ч</p></div>
            <span className="chat-open">Открыть переписку →</span>
          </a>
        ))}
      </section>
    </main>
  );
}
