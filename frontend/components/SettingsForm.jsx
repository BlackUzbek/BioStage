import { useEffect, useState } from "react";
import api from "../services/api";

const emptyForm = { channel_id: "", link: "https://example.com", style: "plain", target_text: "BioStage", is_active: true };

export default function SettingsForm({ onChannelChange }) {
  const [channels, setChannels] = useState([]);
  const [selectedChannelId, setSelectedChannelId] = useState("");
  const [form, setForm] = useState(emptyForm);

  const loadChannels = async () => {
    const { data } = await api.get("/channels");
    setChannels(data);
    if (data.length > 0) {
      const first = data[0];
      setSelectedChannelId(first.channel_id);
      setForm(first);
      onChannelChange(first.channel_id);
    }
  };

  useEffect(() => {
    loadChannels();
  }, []);

  const addChannel = async () => {
    const { data } = await api.post("/channels", { channel_id: form.channel_id, link: form.link, style: form.style, target_text: form.target_text, is_active: true });
    await loadChannels();
    setSelectedChannelId(data.channel_id);
    setForm(data);
    onChannelChange(data.channel_id);
  };

  const updateChannel = async () => {
    const { data } = await api.patch(`/channels/${selectedChannelId}`, {
      link: form.link,
      style: form.style,
      target_text: form.target_text,
      is_active: form.is_active,
    });
    setForm(data);
    await loadChannels();
  };

  const chooseChannel = (id) => {
    setSelectedChannelId(id);
    const channel = channels.find((item) => item.channel_id === id);
    if (channel) {
      setForm(channel);
      onChannelChange(channel.channel_id);
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-md space-y-3">
      <h2 className="text-xl font-semibold">Channels & Settings</h2>

      <input className="w-full border rounded p-2" placeholder="New channel ID" value={form.channel_id} onChange={(e) => setForm({ ...form, channel_id: e.target.value })} />
      <button className="bg-blue-600 text-white px-4 py-2 rounded" onClick={addChannel}>Add Channel</button>

      <select className="w-full border rounded p-2" value={selectedChannelId} onChange={(e) => chooseChannel(e.target.value)}>
        <option value="">Select channel</option>
        {channels.map((channel) => <option key={channel.id} value={channel.channel_id}>{channel.channel_id}</option>)}
      </select>

      <input className="w-full border rounded p-2" placeholder="Link" value={form.link} onChange={(e) => setForm({ ...form, link: e.target.value })} />
      <input className="w-full border rounded p-2" placeholder="Target text" value={form.target_text} onChange={(e) => setForm({ ...form, target_text: e.target.value })} />
      <select className="w-full border rounded p-2" value={form.style} onChange={(e) => setForm({ ...form, style: e.target.value })}>
        <option value="plain">plain</option>
        <option value="bold">bold</option>
        <option value="italic">italic</option>
      </select>
      <label className="flex items-center gap-2">
        <input type="checkbox" checked={Boolean(form.is_active)} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} /> Active
      </label>
      <button className="bg-emerald-600 text-white px-4 py-2 rounded" onClick={updateChannel} disabled={!selectedChannelId}>Save</button>
    </div>
  );
}
