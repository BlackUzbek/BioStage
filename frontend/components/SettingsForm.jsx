import { useEffect, useState } from "react";
import api from "../services/api";

export default function SettingsForm() {
  const [settings, setSettings] = useState({ link: "", style: "plain", target_text: "", channel_id: "" });

  useEffect(() => {
    api.get("/settings").then((res) => setSettings(res.data));
  }, []);

  const save = async () => {
    const { data } = await api.post("/settings/update", settings);
    setSettings(data);
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-md space-y-3">
      <h2 className="text-xl font-semibold">Settings</h2>
      <input className="w-full border rounded p-2" placeholder="Link" value={settings.link} onChange={(e) => setSettings({ ...settings, link: e.target.value })} />
      <input className="w-full border rounded p-2" placeholder="Target text" value={settings.target_text} onChange={(e) => setSettings({ ...settings, target_text: e.target.value })} />
      <input className="w-full border rounded p-2" placeholder="Channel ID" value={settings.channel_id} onChange={(e) => setSettings({ ...settings, channel_id: e.target.value })} />
      <select className="w-full border rounded p-2" value={settings.style} onChange={(e) => setSettings({ ...settings, style: e.target.value })}>
        <option value="plain">plain</option>
        <option value="bold">bold</option>
        <option value="italic">italic</option>
      </select>
      <button className="bg-emerald-600 text-white px-4 py-2 rounded" onClick={save}>Save</button>
    </div>
  );
}
