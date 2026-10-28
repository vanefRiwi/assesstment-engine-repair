import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";
import type { Role } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { Alert, Spinner } from "./ui";

/** Guards routes in the UI. The APIs still enforce authentication and roles on every request. */
export function RequireAuth({ children, role }: { children: ReactNode; role?: Role }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) return <Spinner label="Verificando sesión…" />;
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  if (role && user.role !== role) return <Alert>No tienes permiso para ver esta sección.</Alert>;
  return <>{children}</>;
}
