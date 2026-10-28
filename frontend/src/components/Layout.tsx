import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export function Layout() {
  const { user, logout } = useAuth();
  const links = [
    { to: "/", label: "Dashboard" },
    { to: "/orders", label: "Órdenes" },
    { to: "/clients", label: "Clientes" },
    { to: "/engines", label: "Motores" },
    ...(user?.role === "ADMIN" ? [{ to: "/users", label: "Usuarios" }] : []),
  ];

  return (
    <div className="app">
      <header className="topbar">
        <span className="brand">⚙ Taller de motores</span>
        <nav>
          {links.map((link) => (
            <NavLink key={link.to} to={link.to} end={link.to === "/"}>
              {link.label}
            </NavLink>
          ))}
        </nav>
        <div className="user-box">
          <span>
            {user?.name} · {user?.role === "ADMIN" ? "Administrador" : "Operador"}
          </span>
          <button className="btn btn-link" onClick={() => logout()}>
            Cerrar sesión
          </button>
        </div>
      </header>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
