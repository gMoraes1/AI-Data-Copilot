// Campo de entrada da pergunta + botão de envio.

import { useState } from "react";

interface Props {
  onSend: (question: string) => void;
  disabled: boolean;
}

export function ChatInput({ onSend, disabled }: Props) {
  const [value, setValue] = useState("");

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!value.trim() || disabled) return;
    onSend(value);
    setValue("");
  };

  return (
    <form className="chat-input" onSubmit={submit}>
      <input
        type="text"
        value={value}
        placeholder="Pergunte algo, ex: Quais os 10 clientes que mais compraram?"
        onChange={(e) => setValue(e.target.value)}
        disabled={disabled}
        autoFocus
      />
      <button type="submit" disabled={disabled || !value.trim()}>
        Enviar
      </button>
    </form>
  );
}
