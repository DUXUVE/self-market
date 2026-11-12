import { useEffect, useState } from "react";
import { useParams } from "react-router";
import { getPublicUser, getUserReviews, type PublicUser, type Review } from "../lib/api";

export function meta() {
  return [{ title: "Профиль участника — Self Market" }];
}

export default function UserDetailPage() {
  const { userId } = useParams();
  const [user, setUser] = useState<PublicUser | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [message, setMessage] = useState("Загружаем профиль…");

  useEffect(() => {
    const id = Number(userId);
    const token = window.localStorage.getItem("self-market-token") || "";
    if (!token) {
      setMessage("Войдите в аккаунт, чтобы посмотреть профиль.");
      return;
    }
    Promise.all([getPublicUser(id, token), getUserReviews(id)])
      .then(([profile, userReviews]) => {
        setUser(profile);
        setReviews(userReviews);
        setMessage("");
      })
      .catch((error) => setMessage(error instanceof Error ? error.message : "Не удалось загрузить профиль"));
  }, [userId]);

  if (!user) {
    return <main className="app-shell"><header className="topbar"><a className="brand" href="/">self<span>.</span>market</a><a className="text-button" href="/">На главную</a></header><p className="notice">{message}</p></main>;
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">self<span>.</span>market</a>
        <nav className="main-nav"><a href="/">Заказы</a><a href="/services">Услуги</a><a href="/chats">Сообщения</a><a href="/profile">Профиль</a></nav>
        <a className="text-button" href="/">На главную</a>
      </header>

      <section className="page-intro">
        <p className="eyebrow">УЧАСТНИК SELF MARKET</p>
        <h1>{user.name}</h1>
        <p className="muted">{user.city}</p>
      </section>

      <section className="public-profile-layout">
        <aside className="profile-summary">
          <div className="avatar-placeholder">{user.name.trim().charAt(0).toUpperCase()}</div>
          <h2>{user.name}</h2>
          <p className="muted">{user.city}</p>
          <div className="profile-stats">
            <div><strong>{user.rating_average.toFixed(1)}</strong><span>средний рейтинг</span></div>
            <div><strong>{user.reviews_count}</strong><span>отзывов</span></div>
            <div><strong>{user.total_hours_worked}</strong><span>часов получено</span></div>
          </div>
          {user.first_service && <div className="public-service"><span>Предлагает услугу</span><strong>{user.first_service.title}</strong><small>{user.first_service.price} ч</small></div>}
        </aside>

        <section className="reviews-section">
          <div className="section-heading"><div><p className="eyebrow">ОТЗЫВЫ</p><h2>Что говорят о пользователе</h2></div><span className="count">{reviews.length}</span></div>
          {reviews.length === 0 ? <div className="empty-state"><span>☆</span><h3>Пока нет отзывов</h3><p>Отзывы появятся здесь после завершённых обменов.</p></div> :
            <div className="review-list">{reviews.map((review) => <article className="review-card" key={review.id}>
              <div className="review-card-top"><strong>{review.reviewer_id ? `Участник #${review.reviewer_id}` : "Участник"}</strong><span>{"★".repeat(review.rate)}{"☆".repeat(5 - review.rate)}</span></div>
              {review.comment && <p>{review.comment}</p>}
              {review.order_id && <small>Заказ #{review.order_id}</small>}
            </article>)}</div>}
        </section>
      </section>
    </main>
  );
}
