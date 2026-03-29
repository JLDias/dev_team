// ─── Schemas para geração de Flows Kestra ──────────────────────────────────

enum KestraTaskType {
  Http           // io.kestra.plugin.core.http.Request
  Python         // io.kestra.plugin.scripts.python.Script
  BashScript     // io.kestra.plugin.scripts.shell.Commands
  SubflowExec    // io.kestra.plugin.core.flow.Subflow
  PostgresQuery  // io.kestra.plugin.jdbc.postgresql.Query
  SupabaseHttp   // chamada HTTP para Supabase REST API
  FlowCondition  // io.kestra.plugin.core.flow.If
  Parallel       // io.kestra.plugin.core.flow.Parallel
  Trigger        // webhook / schedule / file detection
}

class KestraInput {
  name string
  type string        // STRING, INT, BOOL, ARRAY, etc.
  description string
  required bool
  default_value string?
}

class KestraFlowTask {
  id string           // snake_case único dentro do flow
  type KestraTaskType
  description string
  depends_on string[] // ids de tasks anteriores
  config_hint string  // resumo do bloco YAML desta task
}

class KestraFlow {
  id string                // namespace/flow-id no formato kestra
  flow_namespace string    // ✅ renomeado de 'namespace' (palavra reservada BAML)
  description string
  inputs KestraInput[]
  tasks KestraFlowTask[]
  triggers string[]        // descrição dos triggers (webhook, cron, etc.)
  labels string[]          // ex: ["crew", "ai", "supabase"]
}

class KestraFlowYAML {
  flow KestraFlow
  yaml_content string   // YAML completo pronto para colocar em kestra_flows/
  filename string       // nome sugerido: namespace.flow-id.yml
}

// ─── Funções ────────────────────────────────────────────────────────────────

function DesignKestraFlow(objective: string, context: string) -> KestraFlow {
  client CustomGemini25Pro
  prompt #"
    Você é um especialista em Kestra (orquestrador de workflows open-source).
    Com base no objetivo abaixo, projete um flow Kestra completo.

    Regras:
    - Namespace deve seguir o padrão: equipe_qwen.<domínio>
    - IDs de tasks em snake_case
    - Sempre inclua inputs para os parâmetros variáveis
    - Prefira tasks Python para lógica de negócio
    - Para Supabase, use chamadas HTTP REST (não driver JDBC direto)
    - Inclua labels relevantes

    Objetivo do flow:
    {{ objective }}

    Contexto adicional (integrações disponíveis, tabelas, endpoints):
    {{ context }}

    {{ ctx.output_format }}
  "#
}

function GenerateKestraFlowYAML(objective: string, context: string) -> KestraFlowYAML {
  client CustomGemini25Pro
  prompt #"
    Você é um especialista em Kestra. Gere um flow YAML completo e funcional.

    Regras de geração:
    - Namespace: equipe_qwen.<domínio>
    - Use plugins oficiais: io.kestra.plugin.core.*, io.kestra.plugin.scripts.python.Script,
      io.kestra.plugin.jdbc.postgresql.*
    - Para chamar a crew CrewAI, use io.kestra.plugin.core.http.Request (POST no endpoint local)
    - Variáveis de ambiente sensíveis via {{ "{{" }} envs.NOME_VAR {{ "}}" }}
    - Inputs Kestra via {{ "{{" }} inputs.nome {{ "}}" }}
    - O YAML deve ser válido e completo, pronto para ser salvo em kestra_flows/

    Objetivo:
    {{ objective }}

    Contexto:
    {{ context }}

    {{ ctx.output_format }}
  "#
}

// ─── Testes ────────────────────────────────────────────────────────────────

test design_crew_trigger_flow {
  functions [DesignKestraFlow]
  args {
    objective #"
      Flow que recebe um webhook com o input da tarefa de desenvolvimento,
      dispara a crew de agentes via HTTP POST, aguarda o resultado e persiste
      o CrewOutput em uma tabela do Supabase PostgreSQL.
    "#
    context #"
      - Crew exposta em http://localhost:8000/run (POST, body: {"task": "..."})
      - Supabase project: local (http://localhost:54321)
      - Tabela destino: crew_runs (id, created_at, input, output, status)
      - Variáveis disponíveis: SUPABASE_URL, SUPABASE_SERVICE_KEY
    "#
  }
}
