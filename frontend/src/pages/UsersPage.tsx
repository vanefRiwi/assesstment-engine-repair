import { useState, type FormEvent } from "react";
import { authApi } from "../api/auth-api";
import type { Role, User } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { ActiveBadge, Alert, InputField, PageHeader, SelectField, Spinner } from "../components/ui";
import { apiFieldErrors, errorMessage, userSchema, validate, type FieldErrors } from "../lib/forms";
import { formatDate } from "../lib/labels";
import { useAsync } from "../lib/useAsync";

const ROLE_OPTIONS = [
  { value: "OPERATOR", label: "Operador" },
  { value: "ADMIN", label: "Administrador" },
];
const EMPTY = { name: "", email: "", password: "", role: "OPERATOR" };

export function UsersPage() {
  const { user: me } = useAuth();
  const users = useAsync(() => authApi.listUsers(), []);
  const [values, setValues] = useState(EMPTY);
  const [errors, setErrors] = useState<FieldErrors>({});
  const [message, setMessage] = useState<{ kind: "success" | "error"; text: string } | null>(null);
  const [saving, setSaving] = useState(false);

  async function run(action: () => Promise<unknown>, successText: string) {
    setSaving(true);
    setMessage(null);
    try {
      await action();
      setMessage({ kind: "success", text: successText });
      await users.reload();
    } catch (err) {
      setErrors(apiFieldErrors(err));
      setMessage({ kind: "error", text: errorMessage(err) });
    } finally {
      setSaving(false);
    }
  }

  function handleCreate(event: FormEvent) {
    event.preventDefault();
    const result = validate(userSchema, values);
    setErrors(result.errors ?? {});
    if (!result.data) return;
    const data = result.data;
    void run(async () => {
      await authApi.createUser(data);
      setValues(EMPTY);
    }, `Usuario ${data.email} creado.`);
  }

  const field = (name: keyof typeof EMPTY) => ({
    name,
    value: values[name],
    error: errors[name],
    onChange: (e: { target: { value: string } }) => setValues({ ...values, [name]: e.target.value }),
  });

  const toggleRole = (user: User) =>
    run(() => authApi.updateUser(user.id, { role: (user.role === "ADMIN" ? "OPERATOR" : "ADMIN") as Role }), "Rol actualizado.");
  const toggleActive = (user: User) =>
    run(() => authApi.setUserStatus(user.id, !user.is_active), user.is_active ? "Usuario desactivado." : "Usuario activado.");

  return (
    <>
      <PageHeader title="Administración de usuarios" />
      {message && <Alert kind={message.kind}>{message.text}</Alert>}
      <form className="card" onSubmit={handleCreate} noValidate>
        <h2>Crear usuario</h2>
        <div className="grid">
          <InputField label="Nombre *" {...field("name")} />
          <InputField label="Correo *" type="email" autoComplete="off" {...field("email")} />
          <InputField label="Contraseña inicial *" type="password" autoComplete="new-password" {...field("password")} />
          <SelectField label="Rol *" options={ROLE_OPTIONS} {...field("role")} />
        </div>
        <div className="form-actions">
          <button className="btn" type="submit" disabled={saving}>Crear usuario</button>
        </div>
      </form>
      <div className="card">
        {users.error && <Alert>{users.error}</Alert>}
        {users.loading ? (
          <Spinner />
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Correo</th>
                  <th>Rol</th>
                  <th>Estado</th>
                  <th>Creado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {users.data?.map((user) => (
                  <tr key={user.id}>
                    <td>{user.name}</td>
                    <td>{user.email}</td>
                    <td>{user.role === "ADMIN" ? "Administrador" : "Operador"}</td>
                    <td><ActiveBadge active={user.is_active} /></td>
                    <td>{formatDate(user.created_at)}</td>
                    <td>
                      {user.id !== me?.id && (
                        <>
                          <button className="btn-link" disabled={saving} onClick={() => toggleRole(user)}>
                            {user.role === "ADMIN" ? "Hacer operador" : "Hacer admin"}
                          </button>
                          {" · "}
                          <button className="btn-link" disabled={saving} onClick={() => toggleActive(user)}>
                            {user.is_active ? "Desactivar" : "Activar"}
                          </button>
                        </>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}
