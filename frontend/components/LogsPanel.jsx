import { useEffect, useState } from "react";
import api from "../services/api";

export default function LogsPanel() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    api.get("/logs").then((res) => setLogs(res.data));
  }, []);

  return (
    <div className="bg-white p-6 rounded-xl shadow-md">
      <h2 className="text-xl font-semibold mb-3">Live Logs</h2>
      <ul className="space-y-2 text-sm">
        {logs.map((log) => (
          <li key={log.id} className="border rounded p-2">
            #{log.message_id} - <b>{log.status}</b> {log.error_text ? `| ${log.error_text}` : ""}
          </li>
        ))}
      </ul>
    </div>
  );
}
