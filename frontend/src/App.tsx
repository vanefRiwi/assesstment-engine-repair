import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { RequireAuth } from "./components/RequireAuth";
import { ClientDetailPage } from "./pages/ClientDetailPage";
import { ClientsPage } from "./pages/ClientsPage";
import { DashboardPage } from "./pages/DashboardPage";
import { EngineDetailPage } from "./pages/EngineDetailPage";
import { EnginesPage } from "./pages/EnginesPage";
import { LoginPage } from "./pages/LoginPage";
import { OrderCreatePage } from "./pages/OrderCreatePage";
import { OrderDetailPage } from "./pages/OrderDetailPage";
import { OrdersPage } from "./pages/OrdersPage";
import { UsersPage } from "./pages/UsersPage";

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <RequireAuth>
            <Layout />
          </RequireAuth>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="clients" element={<ClientsPage />} />
        <Route path="clients/:id" element={<ClientDetailPage />} />
        <Route path="engines" element={<EnginesPage />} />
        <Route path="engines/:id" element={<EngineDetailPage />} />
        <Route path="orders" element={<OrdersPage />} />
        <Route path="orders/new" element={<OrderCreatePage />} />
        <Route path="orders/:id" element={<OrderDetailPage />} />
        <Route
          path="users"
          element={
            <RequireAuth role="ADMIN">
              <UsersPage />
            </RequireAuth>
          }
        />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
