import { useEffect, useState } from "react";
import { useParams } from "react-router";
import { applyToOrder, getCategories, getMe, getOrder, type Category, type Order } from "../lib/api";

export function meta() {
  return [{ title: "Заказ — Self Market" }];
}

export default function OrderDetailPage() {
  const { orderId } = useParams();
  const [order, setOrder] = useState<Order | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [userId, setUserId] = useState<number | null>(null);
  const [token, setToken] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const savedToken = window.localStorage.getItem("self-market-token") || "";
    setToken(savedToken);
    Promise.all([
      getOrder(Number(orderId)),
      getCategories(),
      savedToken ? getMe(savedToken) : Promise.resolve(null),
    ]).then(([orderData, categoryList, user]) => {
      setOrder(orderData);
      setCategories(categoryList);
      setUserId(user?.id ?? null);
    }).catch((error) => setMessage(error instanceof Error ? error.message : "Не удалось загрузить заказ"));
  }, [orderId]);

  async function handleApply() {
    if (!token) {
      setMessage("Чтобы откликнуться, сначала войдите в аккаунт.");
      return;
    }
    setBusy(true);
    setMessage("");
    try {
      await applyToOrder(Number(orderId), token);
      setMessage("Отклик отправлен! Заказчик сможет увидеть вашу заявку.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Не удалось отправить отклик");
    } finally {
      setBusy(false);
    }
  }

  if (!order) {
    return <main className="app-shell"><header className="topbar"><a className="brand" href="/">self<span>.</span>market</a><a className="text-button" href="/">На главную</a></header><p className="muted">{message || "Загружаем заказ…"}</p></main>;
  }

  const category = categories.find((item) => item.id === order.category_id)?.title ?? "Другое";

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">self<span>.</span>market</a>
        <nav className="main-nav"><a className="active" href="/">Заказы</a><a href="/services">Услуги</a><a href="/profile">Профиль</a></nav>
        <a className="text-button" href="/">Назад к заказам</a>
      </header>
      <section className="page-intro">
        <p className="eyebrow">ЗАКАЗ #{order.id}</p>
        <p className="muted">{category} · {order.city}</p>
      </section>
      <article className="order-detail-card">
        <div className="order-meta"><span>{category}</span><span>{order.city}</span></div>
        <h1>{order.title}</h1>
        <p className="order-detail-description">{order.description}</p>
        <div className="order-detail-info">
          <span>Стоимость: {order.price} ч</span>
          <span>Заказчик #{order.user_id}</span>
          <span>{order.contractor_id === null ? "Ищет исполнителя" : "Исполнитель назначен"}</span>
          {order.desired_date && <span>Желаемая дата: {new Date(order.desired_date).toLocaleString("ru-RU")}</span>}
        </div>
        {message && <p className="notice">{message}</p>}
        <div className="details-actions">
          {userId === order.user_id ? <span className="muted">Это ваш заказ</span> :
            order.contractor_id === null ? <button className="primary-button" onClick={handleApply} disabled={busy}>{busy ? "Отправляем…" : "Откликнуться на заказ"}</button> :
            <span className="muted">На этот заказ уже назначен исполнитель.</span>}
          <a className="back-link" href="/">К списку заказов</a>
        </div>
      </article>
    </main>
  );
}
