import { useState } from "react";
import api from "../services/api";

export default function PreviewPanel({ channelId }) {
  const [text, setText] = useState("");
  const [preview, setPreview] = useState("");

  const runPreview = async () => {
    if (!channelId) return;
    const { data } = await api.post("/preview", { text, channel_id: channelId });
    setPreview(data.preview);
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-md space-y-3">
      <h2 className="text-xl font-semibold">Test Preview</h2>
      <p className="text-xs text-slate-500">Channel: {channelId || "not selected"}</p>
      <textarea className="w-full border rounded p-2" rows={4} value={text} onChange={(e) => setText(e.target.value)} />
      <button className="bg-violet-600 text-white px-4 py-2 rounded" onClick={runPreview} disabled={!channelId}>Render</button>
      <div className="border rounded p-2" dangerouslySetInnerHTML={{ __html: preview }} />
    </div>
  );
}
