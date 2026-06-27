// Bloco expansível com o SQL gerado — transparência para o usuário técnico.

interface Props {
  sql: string;
  latencyMs?: number;
}

export function SqlDetails({ sql, latencyMs }: Props) {
  return (
    <details className="sql-details">
      <summary>
        Ver SQL gerado{latencyMs !== undefined ? ` · ${latencyMs} ms` : ""}
      </summary>
      <pre>
        <code>{sql}</code>
      </pre>
    </details>
  );
}
