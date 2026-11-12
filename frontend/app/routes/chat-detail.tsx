import { useEffect, useState } from "react";
import { useParams } from "react-router";
import { getChatMessages, getMe, getOrder, sendChatMessage, type ChatMessage, type Order, type User } from "../lib/api";

export function meta() {
  return [{ title: "Переписка — Self Market" }];
}

export default function ChatDetailPage() {
  const { chatId } = useParams();
  const [token, setToken] = useState("");
  const [user, setUser] = useState<User | null>(null);
  const [order, setOrder] = useState<Order | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [notice, setNotice] = useState("Загружаем переписку…");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const savedToken = window.localStorage.getItem("self-market-token") || "";
    setToken(savedToken);
    if (!savedToken) {
      setNotice("Чтобы открыть переписку, войдите в аккаунт.");
      return;
    }
    Promise.all([getMe(savedToken), getChatMessages(Number(chatId), savedToken)]).then(async ([profile, chatMessages]) => {
      setUser(profile);
      setMessages(chatMessages);
      if (chatMessages.length) {
        const firstMessage = chatMessages[0];
        // The order is loaded from the chat list's order link when available.
        setNotice("");
      } else {
        setNotice("Пока нет сообщений. Начните разговор.");
      }
    }).catch((error) => setNotice(error instanceof Error ? error.message : "Не удалось загрузить переписку"));
  }, [chatId]);

  async function handleSend(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!draft.trim() || !token) return;
    setBusy(true);
    setNotice("");
    try {
      const sent = await sendChatMessage(Number(chatId), draft.trim(), token);
      setMessages((current) => [...current, sent]);
      setDraft("");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Не удалось отправить сообщение");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">self<span>.</span>market</a>
        <nav className="main-nav"><a href="/">Заказы</a><a href="/services">Услуги</a><a className="active" href="/chats">Сообщения</a><a href="/profile">Профиль</a></nav>
        <a className="text-button" href="/chats">Все сообщения</a>
      </header>
      <section className="page-intro"><p className="eyebrow">ПЕРЕПИСКА</p><h1>Чат по заказу</h1><p className="muted">Обсудите детали и договоритесь о помощи.</p></section>
      <section className="chat-window">
        <div className="chat-messages">
          {messages.map((item) => (
            <div className={item.user_id === user?.id ? "chat-message mine" : "chat-message"} key={item.id}>
              <span>{item.user_id === user?.id ? "Вы" : `Участник #${item.user_id}`}</span>
              <p>{item.message_text}</p>
            </div>
          ))}
          {!messages.length && <p className="muted">Здесь пока пусто. Напишите первое сообщение.</p>}
        </div>
        {notice && <p className="notice">{notice}</p>}
        <form className="chat-compose" onSubmit={handleSend}>
          <input value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Напишите сообщение…" maxLength={5000} required />
          <button className="primary-button" disabled={busy || !draft.trim()}>{busy ? "Отправляем…" : "Отправить"}</button>
        </form>
      </section>
    </main>
  );
}
