import { useEffect, useState } from "react";
import { useParams } from "react-router";
import {
  applyToOrder,
  createReview,
  getCategories,
  getMe,
  getOrder,
  getUserReviews,
  getWalletOperations,
  type Category,
  type Order,
  type Review,
  type User,
  type WalletOperation,
} from "../lib/api";

export function meta() {
  return [{ title: "Заказ — Self Market" }];
}

export default function OrderDetailPage() {
  const { orderId } = useParams();
  const [order, setOrder] = useState<Order | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState("");
  const [operations, setOperations] = useState<WalletOperation[]>([]);
  const [contractorReviews, setContractorReviews] = useState<Review[]>([]);
  const [rate, setRate] = useState("5");
  const [comment, setComment] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const savedToken = window.localStorage.getItem("self-market-token") || "";
    setToken(savedToken);
    Promise.all([
      getOrder(Number(orderId)),
      getCategories(),
      savedToken ? getMe(savedToken) : Promise.resolve(null),
    ]).then(async ([orderData, categoryList, currentUser]) => {
      setOrder(orderData);
      setCategories(categoryList);
      setUser(currentUser);
      if (savedToken && currentUser) {
        const history = await getWalletOperations(savedToken);
        setOperations(history.filter((item) => item.order_id === orderData.id));
      }
      if (orderData.contractor_id !== null) {
        const reviews = await getUserReviews(orderData.contractor_id);
        setContractorReviews(reviews);
      }
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

  async function handleReview(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !order) return;
    setBusy(true);
    setMessage("");
    try {
      await createReview(order.id, Number(rate), comment, token);
      setMessage("Спасибо! Ваш отзыв сохранён.");
      if (order.contractor_id !== null) {
        const reviews = await getUserReviews(order.contractor_id);
        setContractorReviews(reviews);
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Не удалось сохранить отзыв");
    } finally {
      setBusy(false);
    }
  }

  if (!order) {
    return <main className="app-shell"><header className="topbar"><a className="brand" href="/">self<span>.</span>market</a><a className="text-button" href="/">На главную</a></header><p className="muted">{message || "Загружаем заказ…"}</p></main>;
  }

  const category = categories.find((item) => item.id === order.category_id)?.title ?? "Другое";
  const operation = operations[0];
  const existingReview = contractorReviews.some((review) => review.order_id === order.id);
  const canReview = user?.id === order.user_id && operation?.status === "completed" && !existingReview;

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">self<span>.</span>market</a>
        <nav className="main-nav"><a className="active" href="/">Заказы</a><a href="/services">Услуги</a><a href="/chats">Сообщения</a><a href="/profile">Профиль</a></nav>
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
        {order.contractor_id !== null && <p className="muted">Исполнитель: <a className="back-link" href={`/users/${order.contractor_id}`}>Посмотреть профиль и отзывы →</a></p>}
        {message && <p className="notice">{message}</p>}
        <div className="details-actions">
          {user?.id === order.user_id ? <span className="muted">Это ваш заказ</span> :
            order.contractor_id === null ? <button className="primary-button" onClick={handleApply} disabled={busy}>{busy ? "Отправляем…" : "Откликнуться на заказ"}</button> :
            <span className="muted">На этот заказ уже назначен исполнитель.</span>}
          <a className="back-link" href="/">К списку заказов</a>
        </div>
      </article>

      {user?.id === order.user_id && operation?.status === "awaiting_confirmation" &&
        <section className="review-form-card"><h2>Заказ ожидает подтверждения</h2><p className="muted">Исполнитель отметил заказ выполненным. После подтверждения можно будет оставить отзыв.</p></section>}

      {canReview && <section className="review-form-card">
        <p className="eyebrow">ОБРАТНАЯ СВЯЗЬ</p><h2>Оцените исполнителя</h2>
        <p className="muted">Расскажите, как прошёл обмен. Отзыв будет виден в профиле исполнителя.</p>
        <form className="auth-form" onSubmit={handleReview}>
          <label>Оценка
            <select className="form-select" value={rate} onChange={(event) => setRate(event.target.value)}>
              <option value="5">5 — Отлично</option><option value="4">4 — Хорошо</option><option value="3">3 — Нормально</option><option value="2">2 — Плохо</option><option value="1">1 — Очень плохо</option>
            </select>
          </label>
          <label>Комментарий<textarea className="form-textarea" rows={4} value={comment} onChange={(event) => setComment(event.target.value)} placeholder="Поделитесь впечатлениями (необязательно)" /></label>
          <button className="primary-button" disabled={busy}>{busy ? "Отправляем…" : "Оставить отзыв"}</button>
        </form>
      </section>}

      {user?.id === order.user_id && existingReview && <section className="review-form-card"><h2>Отзыв уже оставлен</h2><p className="muted">Спасибо, что поделились впечатлениями об обмене.</p></section>}
    </main>
  );
}
