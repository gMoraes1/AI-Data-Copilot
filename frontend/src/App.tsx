import { useEffect, useRef } from "react";
import { useAuth } from "./auth/AuthContext";
import { ChatInput } from "./components/ChatInput";
import { LoginScreen } from "./components/LoginScreen";
import { MessageBubble } from "./components/MessageBubble";
import { useChat } from "./hooks/useChat";

const SUGESTOES = [
  "Quais foram os 10 clientes que mais compraram?",
  "Qual o faturamento dos últimos meses?",
  "Quantos pedidos estão atrasados?",
];

export default function App() {
  const { user, loading, logout } = useAuth();
  const { turns, loading: chatLoading, send } = useChat();
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [turns]);

  if (loading) {
    return <div className="app centered">Carregando…</div>;
  }

  if (!user) {
    return <LoginScreen />;
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Corporate AI Copilot</h1>
          <p>Consulte os dados da empresa em linguagem natural.</p>
        </div>
        <div className="user-box">
          <span>{user.full_name || user.email}</span>
          {user.tenant_name && <span className="tenant-badge">{user.tenant_name}</span>}
          <button className="link-button" onClick={logout}>
            Sair
          </button>
        </div>
      </header>

      <main className="chat">
        {turns.length === 0 ? (
          <div className="empty-state">
            <p>Comece com uma das perguntas:</p>
            <div className="suggestions">
              {SUGESTOES.map((s) => (
                <button key={s} onClick={() => send(s)} disabled={chatLoading}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          turns.map((turn) => <MessageBubble key={turn.id} turn={turn} />)
        )}
        <div ref={endRef} />
      </main>

      <footer className="footer">
        <ChatInput onSend={send} disabled={chatLoading} />
      </footer>
    </div>
  );
}
