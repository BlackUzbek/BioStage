import { useState } from "react";
import api, { setToken } from "../services/api";

export default function LoginForm({ onSuccess }) {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");

  const submit = async (event) => {
    event.preventDefault();
    try {
      const { data } = await api.post("/auth/login", { username, password });
      setToken(data.access_token);
      onSuccess();
    } catch (e) {
      setError(e.response?.data?.detail || "Login failed");
    }
  };

  return (
    <form onSubmit={submit} className="bg-white p-6 rounded-xl shadow-md space-y-3">
      <h2 className="text-xl font-semibold">Admin Login</h2>
      <input className="w-full border rounded p-2" value={username} onChange={(e) => setUsername(e.target.value)} />
      <input className="w-full border rounded p-2" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      {error && <p className="text-red-500 text-sm">{error}</p>}
      <button className="w-full bg-blue-600 text-white py-2 rounded">Login</button>
    </form>
  );
}
