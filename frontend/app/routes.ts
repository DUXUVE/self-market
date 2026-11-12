import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("services", "routes/services.tsx"),
  route("profile", "routes/profile.tsx"),
  route("orders/new", "routes/create-order.tsx"),
  route("orders/:orderId", "routes/order-detail.tsx"),
] satisfies RouteConfig;
