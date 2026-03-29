// ─── Schemas do Dev Team CrewAI ────────────────────────────────────────────

enum AgentRole {
  SuperDev
  PythonExpert
  BAMLExpert
  LangGraphExpert
  RAGExpert
  SupabaseExpert
  KestraExpert
  QualitySupervisor
}

enum TaskStatus {
  Pending
  InProgress
  Done
  Rejected
}

enum CodeLanguage {
  Python
  YAML
  SQL
  BAML
  TypeScript
  Markdown
}

// ─── Artefato de código gerado por um agente ───────────────────────────────

class CodeArtifact {
  filename string
  language CodeLanguage
  content string
  description string
  dependencies string[]
}

// ─── Tarefa de desenvolvimento estruturada ─────────────────────────────────

class DevelopmentTask {
  title string
  description string
  assigned_to AgentRole
  expected_output string
  acceptance_criteria string[]
  dependencies string[]  // títulos de outras tasks que devem ser concluídas antes
}

// ─── Resultado produzido por um agente ─────────────────────────────────────

class AgentTaskResult {
  agent AgentRole
  task_title string
  status TaskStatus
  summary string
  artifacts CodeArtifact[]
  observations string[]    // notas técnicas relevantes
  next_steps string[]
}

// ─── Revisão de qualidade final ────────────────────────────────────────────

class QualityReview {
  approved bool
  score int           // 0-100
  summary string
  issues string[]
  recommendations string[]
  reviewed_artifacts string[]   // filenames revisados
}

// ─── Output consolidado da crew ────────────────────────────────────────────

class CrewOutput {
  objective string
  tasks AgentTaskResult[]
  quality_review QualityReview
  final_deliverables CodeArtifact[]
}

// ─── Funções ────────────────────────────────────────────────────────────────

function ParseDevelopmentTask(raw_task: string) -> DevelopmentTask {
  client CustomGemini25Pro
  prompt #"
    Analise a descrição abaixo e extraia uma tarefa de desenvolvimento estruturada.
    Identifique claramente: título, descrição técnica, agente mais adequado para executar,
    critérios de aceite e dependências com outras tarefas.

    Descrição:
    {{ raw_task }}

    {{ ctx.output_format }}
  "#
}

function ReviewCodeQuality(artifacts: string, criteria: string) -> QualityReview {
  client CustomGemini25Pro
  prompt #"
    Você é um supervisor de qualidade de software sênior.
    Avalie os artefatos abaixo com base nos critérios fornecidos.
    Seja objetivo e técnico. Pontue de 0 a 100.

    Artefatos:
    {{ artifacts }}

    Critérios de aceite:
    {{ criteria }}

    {{ ctx.output_format }}
  "#
}

function SummarizeCrewRun(raw_output: string) -> CrewOutput {
  client CustomGemini25Pro
  prompt #"
    Analise o log de execução de uma crew de agentes de IA e estruture o resultado.
    Identifique cada agente, suas entregas, artefatos produzidos e o resultado da revisão de qualidade.

    Log de execução:
    {{ raw_output }}

    {{ ctx.output_format }}
  "#
}

// ─── Testes ────────────────────────────────────────────────────────────────

test parse_simple_task {
  functions [ParseDevelopmentTask]
  args {
    raw_task #"
      Criar um flow Kestra que dispara a crew de agentes toda vez que um novo arquivo
      for depositado no bucket do Supabase Storage. O flow deve passar o caminho do arquivo
      como input para a crew e salvar o resultado em uma tabela PostgreSQL.
      Depende da configuração do bucket no Supabase e do endpoint HTTP da crew.
    "#
  }
}
