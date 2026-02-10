import { useState } from "react";
import LoginForm from "../components/LoginForm";
import LogsPanel from "../components/LogsPanel";
import PreviewPanel from "../components/PreviewPanel";
import SettingsForm from "../components/SettingsForm";

export default function Home() {
  const [authenticated, setAuthenticated] = useState(false);
  const [selectedChannelId, setSelectedChannelId] = useState("");

  if (!authenticated) {
    return (
      <main className="min-h-screen flex items-center justify-center p-6">
        <LoginForm onSuccess={() => setAuthenticated(true)} />
      </main>
    );
  }

  return (
    <main className="min-h-screen p-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
      <SettingsForm onChannelChange={setSelectedChannelId} />
      <PreviewPanel channelId={selectedChannelId} />
      <div className="lg:col-span-2">
        <LogsPanel />
      </div>
    </main>
  );
}
