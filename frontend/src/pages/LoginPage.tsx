import { useState, type FormEvent } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { z } from "zod";
import { useAuth } from "../auth/AuthContext";
import { Alert, InputField } from "../components/ui";
import { errorMessage, validate, type FieldErrors } from "../lib/forms";

const loginSchema = z.object({
  email: z.string().trim().email("Ingresa un correo válido"),
  password: z.string().min(1, "Ingresa tu contraseña"),
});

export function LoginPage() {
  const { user, login, sessionExpired } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [values, setValues] = useState({ email: "", password: "" });
  const [errors, setErrors] = useState<FieldErrors>({});
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (user) return <Navigate to="/" replace />;

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const result = validate(loginSchema, values);
    setErrors(result.errors ?? {});
    if (!result.data) return;

    setSubmitting(true);
    setError(null);
    try {
      await login(result.data.email, result.data.password);
      navigate((location.state as { from?: string } | null)?.from ?? "/", { replace: true });
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="login-page">
      <form className="card login-card" onSubmit={handleSubmit} noValidate>
        <h1>Taller de motores</h1>
        <p>Ingresa con tu cuenta para continuar.</p>
        {sessionExpired && <Alert kind="info">Tu sesión expiró. Vuelve a iniciar sesión.</Alert>}
        {error && <Alert>{error}</Alert>}
        <InputField
          label="Correo electrónico"
          name="email"
          type="email"
          autoComplete="username"
          value={values.email}
          error={errors.email}
          onChange={(e) => setValues({ ...values, email: e.target.value })}
        />
        <InputField
          label="Contraseña"
          name="password"
          type="password"
          autoComplete="current-password"
          value={values.password}
          error={errors.password}
          onChange={(e) => setValues({ ...values, password: e.target.value })}
        />
        <button className="btn" type="submit" disabled={submitting}>
          {submitting ? "Ingresando…" : "Iniciar sesión"}
        </button>
      </form>
    </div>
  );
}
