// ─── Schemas do Pipeline RAG ───────────────────────────────────────────────

enum DocumentType {
  Code
  Documentation
  FlowYAML
  SchemaBAML
  AgentPrompt
  TaskDescription
  KnowledgeBase
}

enum RetrievalStrategy {
  Semantic        // busca por similaridade vetorial
  Keyword         // busca por palavras-chave (BM25)
  Hybrid          // combinação de semântica + keyword
  GraphRAG        // RAG com grafo de conhecimento
}

// ─── Chunk de documento recuperado ─────────────────────────────────────────

class DocumentChunk {
  id string
  source string          // caminho do arquivo ou URL
  doc_type DocumentType
  content string
  relevance_score float  // 0.0 a 1.0
  metadata string[]      // pares "chave:valor"
}

// ─── Consulta estruturada para o pipeline RAG ──────────────────────────────

class RAGQuery {
  query string
  intent string            // o que o usuário realmente quer encontrar
  filters string[]         // ex: ["doc_type:Code", "language:Python"]
  strategy RetrievalStrategy
  top_k int                // número de chunks a recuperar
  rerank bool              // aplicar reranking após recuperação
}

// ─── Resposta sintetizada pelo RAG ─────────────────────────────────────────

class RAGResponse {
  answer string
  confidence float         // 0.0 a 1.0
  sources DocumentChunk[]
  reasoning string         // como chegou à resposta
  follow_up_questions string[]
  requires_more_context bool
}

// ─── Configuração de um pipeline RAG ──────────────────────────────────────

class RAGPipelineConfig {
  name string
  description string
  embedding_model string         // ex: "text-embedding-3-small"
  vector_store string            // ex: "supabase/pgvector"
  chunk_size int
  chunk_overlap int
  strategy RetrievalStrategy
  reranker string?               // modelo de reranking, se usar
  collection_name string         // nome da tabela/collection no vector store
}

// ─── Avaliação de qualidade de um resultado RAG ────────────────────────────

class RAGEvaluation {
  query string
  response RAGResponse
  faithfulness float       // resposta é fiel às fontes? (0-1)
  relevance float          // fontes são relevantes à query? (0-1)
  completeness float       // resposta cobre tudo necessário? (0-1)
  hallucination_detected bool
  notes string
}

// ─── Funções ────────────────────────────────────────────────────────────────

function ParseRAGQuery(user_input: string, available_filters: string) -> RAGQuery {
  client CustomGemini25Pro
  prompt #"
    Analise a pergunta do usuário e estruture uma consulta otimizada para um pipeline RAG.
    Identifique a intenção real, filtros aplicáveis e a estratégia de busca mais adequada.

    Filtros disponíveis no sistema:
    {{ available_filters }}

    Pergunta do usuário:
    {{ user_input }}

    {{ ctx.output_format }}
  "#
}

function SynthesizeRAGResponse(query: string, retrieved_chunks: string) -> RAGResponse {
  client CustomGemini25Pro
  prompt #"
    Você é um assistente especialista em desenvolvimento de software com IA.
    Com base nos trechos de documentos recuperados, responda à consulta de forma precisa e técnica.

    IMPORTANTE:
    - Baseie a resposta APENAS no conteúdo dos chunks fornecidos
    - Se a informação não estiver nos chunks, indique requires_more_context: true
    - Cite as fontes utilizadas
    - Seja objetivo e técnico

    Consulta:
    {{ query }}

    Chunks recuperados:
    {{ retrieved_chunks }}

    {{ ctx.output_format }}
  "#
}

function EvaluateRAGResult(query: string, response: string, sources: string) -> RAGEvaluation {
  client CustomGemini25Pro
  prompt #"
    Avalie a qualidade desta resposta RAG em relação à consulta e às fontes utilizadas.
    Verifique fidelidade (a resposta reflete as fontes?), relevância (as fontes eram as certas?)
    e completude (a resposta cobre o que foi perguntado?).
    Detecte alucinações: afirmações na resposta que NÃO estão nas fontes.

    Consulta original:
    {{ query }}

    Resposta gerada:
    {{ response }}

    Fontes utilizadas:
    {{ sources }}

    {{ ctx.output_format }}
  "#
}

function DesignRAGPipeline(use_case: string, constraints: string) -> RAGPipelineConfig {
  client CustomGemini25Pro
  prompt #"
    Projete a configuração de um pipeline RAG para o caso de uso descrito.
    O vector store disponível é Supabase com pgvector.
    Considere as restrições de infraestrutura fornecidas.

    Caso de uso:
    {{ use_case }}

    Restrições e contexto:
    {{ constraints }}

    {{ ctx.output_format }}
  "#
}

// ─── Testes ────────────────────────────────────────────────────────────────

test parse_dev_query {
  functions [ParseRAGQuery]
  args {
    user_input "Como configurar um flow Kestra para disparar a crew quando um arquivo chega no Supabase Storage?"
    available_filters #"
      doc_type: Code, Documentation, FlowYAML, SchemaBAML, AgentPrompt, TaskDescription, KnowledgeBase
      language: Python, YAML, SQL, BAML
      agent: super_dev, python_expert, baml_expert, langgraph_expert, rag_expert, supabase_expert, kestra_expert
    "#
  }
}

test design_project_rag {
  functions [DesignRAGPipeline]
  args {
    use_case #"
      Pipeline RAG para a equipe de agentes consultarem a base de conhecimento do projeto:
      prompts dos agentes, flows Kestra existentes, schemas BAML e documentação técnica.
    "#
    constraints #"
      - Supabase local (pgvector habilitado)
      - Documentos em Markdown, Python, YAML e BAML
      - Máximo 500 tokens por chunk
      - Orçamento limitado: preferir embeddings locais ou modelos baratos
    "#
  }
}
