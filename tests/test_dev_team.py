"""
test_dev_team.py — Testes completos para o projeto DevTeamCrew
==============================================================
Cobre:
  1. Teste de inicialização da Crew
  2. Teste de carregamento de prompts e configs
  3. Teste de execução completa (run)
  4. Teste nativo CrewAI (crewai test)
  5. Testes unitários automatizados com pytest + mocks
"""

import os
import sys
import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

# ─────────────────────────────────────────────
# Ajuste de PATH para rodar de qualquer diretório
# ─────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent / "dev_team"
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


# ══════════════════════════════════════════════════════════════════════════════
# TESTE 1 — Inicialização da Crew
# ══════════════════════════════════════════════════════════════════════════════
class TestCrewInitialization(unittest.TestCase):
    """Verifica se a DevTeamCrew é instanciada sem erros."""

    def test_crew_imports_successfully(self):
        """A classe DevTeamCrew deve ser importável."""
        try:
            from dev_team.crew import DevTeamCrew
        except ImportError as e:
            self.fail(f"Falha ao importar DevTeamCrew: {e}")

    def test_crew_instantiates(self):
        """DevTeamCrew() deve ser criado sem exceções."""
        from dev_team.crew import DevTeamCrew
        try:
            crew_instance = DevTeamCrew()
            self.assertIsNotNone(crew_instance)
        except Exception as e:
            self.fail(f"DevTeamCrew() falhou na inicialização: {e}")

    def test_crew_has_agents_config(self):
        """A crew deve ter agents_config definido."""
        from dev_team.crew import DevTeamCrew
        crew = DevTeamCrew()
        self.assertTrue(hasattr(crew, 'agents_config'))
        self.assertIsNotNone(crew.agents_config)

    def test_crew_has_tasks_config(self):
        """A crew deve ter tasks_config definido."""
        from dev_team.crew import DevTeamCrew
        crew = DevTeamCrew()
        self.assertTrue(hasattr(crew, 'tasks_config'))
        self.assertIsNotNone(crew.tasks_config)

    def test_manager_llm_defined(self):
        """O modelo LLM do manager deve estar definido."""
        from dev_team.crew import DevTeamCrew
        crew = DevTeamCrew()
        self.assertTrue(hasattr(crew, 'manager_llm_model'))
        self.assertIn('gemini', crew.manager_llm_model.lower())

    def test_default_llm_defined(self):
        """O modelo LLM padrão deve estar definido."""
        from dev_team.crew import DevTeamCrew
        crew = DevTeamCrew()
        self.assertTrue(hasattr(crew, 'default_llm_model'))
        self.assertIsNotNone(crew.default_llm_model)


# ══════════════════════════════════════════════════════════════════════════════
# TESTE 2 — Carregamento de Prompts e Configs
# ══════════════════════════════════════════════════════════════════════════════
class TestPromptsAndConfigs(unittest.TestCase):
    """Verifica se todos os arquivos de configuração existem e carregam."""

    EXPECTED_AGENTS = [
        'super_dev',
        'python_expert',
        'baml_expert',
        'langgraph_expert',
        'rag_expert',
        'supabase_expert',
        'kestra_expert',
        'quality_supervisor',
    ]

    EXPECTED_TASKS = [
        'development_task',
        'quality_review_task',
    ]

    EXPECTED_PROMPTS = [
        'super_dev.md',
        'python_expert.md',
        'baml_expert.md',
        'langgraph_expert.md',
        'rag_expert.md',
        'supabase_expert.md',
        'kestra_expert.md',
        'quality_supervisor.md',
    ]

    def setUp(self):
        from dev_team.crew import DevTeamCrew
        self.crew = DevTeamCrew()
        self.prompts_path = SRC_PATH / "dev_team" / "prompts"
        self.config_path = SRC_PATH / "dev_team" / "config"

    def test_agents_yaml_exists(self):
        """agents.yaml deve existir na pasta config."""
        agents_yaml = self.config_path / "agents.yaml"
        self.assertTrue(agents_yaml.exists(), f"Não encontrado: {agents_yaml}")

    def test_tasks_yaml_exists(self):
        """tasks.yaml deve existir na pasta config."""
        tasks_yaml = self.config_path / "tasks.yaml"
        self.assertTrue(tasks_yaml.exists(), f"Não encontrado: {tasks_yaml}")

    def test_all_agents_in_yaml(self):
        """Todos os agentes esperados devem estar no agents.yaml."""
        for agent_name in self.EXPECTED_AGENTS:
            self.assertIn(
                agent_name,
                self.crew.agents_dict,
                f"Agente '{agent_name}' não encontrado no agents.yaml"
            )

    def test_all_tasks_in_yaml(self):
        """Todas as tasks esperadas devem estar no tasks.yaml."""
        for task_name in self.EXPECTED_TASKS:
            self.assertIn(
                task_name,
                self.crew.tasks_dict,
                f"Task '{task_name}' não encontrada no tasks.yaml"
            )

    def test_all_prompt_files_exist(self):
        """Todos os arquivos .md de prompt devem existir."""
        for prompt_file in self.EXPECTED_PROMPTS:
            path = self.prompts_path / prompt_file
            self.assertTrue(
                path.exists(),
                f"Arquivo de prompt não encontrado: {path}"
            )

    def test_all_prompts_not_empty(self):
        """Nenhum arquivo de prompt deve estar vazio."""
        for prompt_file in self.EXPECTED_PROMPTS:
            path = self.prompts_path / prompt_file
            if path.exists():
                content = path.read_text(encoding='utf-8')
                self.assertGreater(
                    len(content.strip()), 0,
                    f"Arquivo de prompt vazio: {prompt_file}"
                )

    def test_agents_have_required_fields(self):
        """Cada agente no YAML deve ter 'role' e 'goal'."""
        for agent_name in self.EXPECTED_AGENTS:
            if agent_name in self.crew.agents_dict:
                agent_data = self.crew.agents_dict[agent_name]
                self.assertIn('role', agent_data, f"'{agent_name}' sem 'role'")
                self.assertIn('goal', agent_data, f"'{agent_name}' sem 'goal'")

    def test_tasks_have_required_fields(self):
        """Cada task no YAML deve ter 'description' e 'expected_output'."""
        for task_name in self.EXPECTED_TASKS:
            if task_name in self.crew.tasks_dict:
                task_data = self.crew.tasks_dict[task_name]
                self.assertIn('description', task_data, f"'{task_name}' sem 'description'")
                self.assertIn('expected_output', task_data, f"'{task_name}' sem 'expected_output'")

    def test_load_prompt_function(self):
        """A função load_prompt deve retornar string não vazia."""
        from dev_team.crew import load_prompt
        content = load_prompt('super_dev.md')
        self.assertIsInstance(content, str)
        self.assertGreater(len(content.strip()), 0)

    def test_load_prompt_raises_for_missing_file(self):
        """load_prompt deve lançar FileNotFoundError para arquivo inexistente."""
        from dev_team.crew import load_prompt
        with self.assertRaises(FileNotFoundError):
            load_prompt('arquivo_que_nao_existe.md')

    def test_load_yaml_config_function(self):
        """A função load_yaml_config deve retornar um dicionário."""
        from dev_team.crew import load_yaml_config
        config = load_yaml_config('agents.yaml')
        self.assertIsInstance(config, dict)
        self.assertGreater(len(config), 0)

    def test_load_yaml_raises_for_missing_file(self):
        """load_yaml_config deve lançar FileNotFoundError para arquivo inexistente."""
        from dev_team.crew import load_yaml_config
        with self.assertRaises(FileNotFoundError):
            load_yaml_config('config_que_nao_existe.yaml')


# ══════════════════════════════════════════════════════════════════════════════
# TESTE 3 — Execução Completa (run) com Mock
# ══════════════════════════════════════════════════════════════════════════════
class TestCrewExecution(unittest.TestCase):
    """Testa a execução da crew sem chamar a API real (usando mocks)."""

    @patch('dev_team.crew.Agent')
    @patch('dev_team.crew.Crew')
    def test_run_calls_kickoff(self, mock_crew_class, mock_agent_class):
        """run() deve chamar kickoff() na crew."""
        # Setup mock
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = MagicMock(raw="Resultado mock")
        mock_crew_class.return_value = mock_crew_instance

        from dev_team.main import run
        with patch('dev_team.main.DevTeamCrew') as mock_dev_team:
            mock_crew_obj = MagicMock()
            mock_crew_obj.crew.return_value.kickoff.return_value = MagicMock(
                raw="Resultado mock de execução"
            )
            mock_dev_team.return_value = mock_crew_obj
            result = run()
            mock_crew_obj.crew.return_value.kickoff.assert_called_once()

    @patch('dev_team.main.DevTeamCrew')
    def test_run_passes_correct_inputs(self, mock_dev_team_class):
        """run() deve passar 'topic' e 'current_year' como inputs."""
        mock_crew_obj = MagicMock()
        mock_crew_obj.crew.return_value.kickoff.return_value = MagicMock(raw="ok")
        mock_dev_team_class.return_value = mock_crew_obj

        from dev_team.main import run
        run()

        call_args = mock_crew_obj.crew.return_value.kickoff.call_args
        inputs_passed = call_args[1].get('inputs')
        if not inputs_passed and call_args[0]:
            inputs_passed = call_args[0][0]
        inputs_passed = inputs_passed or {}
        self.assertIn('topic', inputs_passed)
        self.assertIn('current_year', inputs_passed)

    @patch('dev_team.main.DevTeamCrew')
    def test_run_handles_exception(self, mock_dev_team_class):
        """run() deve propagar exceções corretamente."""
        mock_crew_obj = MagicMock()
        mock_crew_obj.crew.return_value.kickoff.side_effect = Exception("API Error simulado")
        mock_dev_team_class.return_value = mock_crew_obj

        from dev_team.main import run
        with self.assertRaises(Exception) as ctx:
            run()
        self.assertIn("API Error simulado", str(ctx.exception))

    @patch('dev_team.main.DevTeamCrew')
    def test_train_function_exists(self, mock_dev_team_class):
        """A função train() deve existir e ser chamável."""
        from dev_team import main
        self.assertTrue(callable(getattr(main, 'train', None)))

    @patch('dev_team.main.DevTeamCrew')
    def test_replay_function_exists(self, mock_dev_team_class):
        """A função replay() deve existir e ser chamável."""
        from dev_team import main
        self.assertTrue(callable(getattr(main, 'replay', None)))

    @patch('dev_team.main.DevTeamCrew')
    def test_test_function_exists(self, mock_dev_team_class):
        """A função test() deve existir e ser chamável."""
        from dev_team import main
        self.assertTrue(callable(getattr(main, 'test', None)))


# ══════════════════════════════════════════════════════════════════════════════
# TESTE 4 — Teste Nativo CrewAI via subprocess
# ══════════════════════════════════════════════════════════════════════════════
class TestCrewAINative(unittest.TestCase):
    """
    Executa o comando 'crewai test' como subprocesso.
    ATENÇÃO: Este teste faz chamadas reais à API Gemini.
    Use apenas quando as chaves de API estiverem configuradas.
    """

    def test_crewai_cli_available(self):
        """O comando 'crewai' deve estar disponível no PATH."""
        import shutil
        crewai_cmd = shutil.which('crewai') or ('crewai.exe' if os.name == 'nt' else 'crewai')
        result = subprocess.run(
            [crewai_cmd, '--version'],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
        )
        self.assertEqual(
            result.returncode, 0,
            f"'crewai' não encontrado ou falhou: {result.stderr}"
        )

    @unittest.skipUnless(
        os.getenv('GEMINI_API_KEY'),
        "Pulando: GEMINI_API_KEY não configurada"
    )
    def test_crewai_native_test_command(self):
        """
        Executa 'crewai test -n 1 -m gemini/gemini-2.5-flash'.
        Requer GEMINI_API_KEY no ambiente.
        """
        import shutil
        crewai_cmd = shutil.which('crewai') or ('crewai.exe' if os.name == 'nt' else 'crewai')
        result = subprocess.run(
            [crewai_cmd, 'test', '-n', '1', '-m', 'gemini/gemini-2.5-flash'],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=300  # 5 minutos de timeout
        )
        self.assertEqual(
            result.returncode, 0,
            f"'crewai test' falhou:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# TESTES UNITÁRIOS AUTOMATIZADOS — Agentes individuais
# ══════════════════════════════════════════════════════════════════════════════
class TestAgentCreation(unittest.TestCase):
    """Testa criação individual de cada agente com mocks."""

    def setUp(self):
        self.patcher_agent = patch('dev_team.crew.Agent')
        self.mock_agent = self.patcher_agent.start()
        self.mock_agent.return_value = MagicMock()

    def tearDown(self):
        self.patcher_agent.stop()

    def _get_crew(self):
        from dev_team.crew import DevTeamCrew
        return DevTeamCrew()

    def test_super_dev_agent_created(self):
        crew = self._get_crew()
        agent = crew.super_dev()
        self.mock_agent.assert_called()
        call_kwargs = self.mock_agent.call_args[1]
        self.assertTrue(call_kwargs.get('allow_delegation', False))
        self.assertEqual(call_kwargs.get('llm'), crew.manager_llm_model)

    def test_python_expert_agent_created(self):
        crew = self._get_crew()
        agent = crew.python_expert()
        self.mock_agent.assert_called()
        call_kwargs = self.mock_agent.call_args[1]
        self.assertEqual(call_kwargs.get('llm'), crew.default_llm_model)

    def test_baml_expert_agent_created(self):
        crew = self._get_crew()
        crew.baml_expert()
        self.mock_agent.assert_called()

    def test_langgraph_expert_agent_created(self):
        crew = self._get_crew()
        crew.langgraph_expert()
        self.mock_agent.assert_called()

    def test_rag_expert_agent_created(self):
        crew = self._get_crew()
        crew.rag_expert()
        self.mock_agent.assert_called()

    def test_supabase_expert_agent_created(self):
        crew = self._get_crew()
        crew.supabase_expert()
        self.mock_agent.assert_called()

    def test_kestra_expert_agent_created(self):
        crew = self._get_crew()
        crew.kestra_expert()
        self.mock_agent.assert_called()

    def test_quality_supervisor_agent_created(self):
        crew = self._get_crew()
        crew.quality_supervisor()
        self.mock_agent.assert_called()


# ══════════════════════════════════════════════════════════════════════════════
# TESTES UNITÁRIOS AUTOMATIZADOS — Tasks
# ══════════════════════════════════════════════════════════════════════════════
class TestTaskCreation(unittest.TestCase):
    """Testa criação de tasks."""

    def setUp(self):
        self.patcher_task = patch('dev_team.crew.Task')
        self.patcher_agent = patch('dev_team.crew.Agent')
        self.mock_task = self.patcher_task.start()
        self.mock_agent = self.patcher_agent.start()
        self.mock_task.return_value = MagicMock()
        self.mock_agent.return_value = MagicMock()

    def tearDown(self):
        self.patcher_task.stop()
        self.patcher_agent.stop()

    def test_development_task_created(self):
        from dev_team.crew import DevTeamCrew
        crew = DevTeamCrew()
        task = crew.development_task()
        self.mock_task.assert_called()
        call_kwargs = self.mock_task.call_args[1]
        self.assertIn('description', call_kwargs)
        self.assertIn('expected_output', call_kwargs)

    def test_quality_review_task_created(self):
        from dev_team.crew import DevTeamCrew
        crew = DevTeamCrew()
        task = crew.quality_review_task()
        self.mock_task.assert_called()
        call_kwargs = self.mock_task.call_args[1]
        self.assertIn('description', call_kwargs)
        self.assertIn('expected_output', call_kwargs)

    def test_development_task_description_not_empty(self):
        from dev_team.crew import DevTeamCrew
        crew = DevTeamCrew()
        crew.development_task()
        call_kwargs = self.mock_task.call_args[1]
        self.assertGreater(len(call_kwargs['description'].strip()), 0)

    def test_quality_review_task_has_agent(self):
        from dev_team.crew import DevTeamCrew
        crew = DevTeamCrew()
        crew.quality_review_task()
        call_kwargs = self.mock_task.call_args[1]
        self.assertIn('agent', call_kwargs)
        self.assertIsNotNone(call_kwargs['agent'])


# ══════════════════════════════════════════════════════════════════════════════
# TESTES UNITÁRIOS AUTOMATIZADOS — Crew completa
# ══════════════════════════════════════════════════════════════════════════════
class TestCrewAssembly(unittest.TestCase):
    """Testa a montagem completa da Crew."""

    @patch('dev_team.crew.Crew')
    @patch('dev_team.crew.Task')
    @patch('dev_team.crew.Agent')
    def test_crew_uses_hierarchical_process(self, mock_agent, mock_task, mock_crew):
        """A crew deve usar Process.hierarchical."""
        from crewai import Process
        from dev_team.crew import DevTeamCrew

        mock_agent.return_value = MagicMock()
        mock_task.return_value = MagicMock()
        mock_crew.return_value = MagicMock()

        crew_instance = DevTeamCrew()
        crew_instance.crew()

        call_kwargs = mock_crew.call_args[1]
        self.assertEqual(call_kwargs.get('process'), Process.hierarchical)

    @patch('dev_team.crew.Crew')
    @patch('dev_team.crew.Task')
    @patch('dev_team.crew.Agent')
    def test_crew_has_manager_agent(self, mock_agent, mock_task, mock_crew):
        """A crew hierárquica deve ter um manager_agent definido."""
        mock_agent.return_value = MagicMock()
        mock_task.return_value = MagicMock()
        mock_crew.return_value = MagicMock()

        from dev_team.crew import DevTeamCrew
        crew_instance = DevTeamCrew()
        crew_instance.crew()

        call_kwargs = mock_crew.call_args[1]
        self.assertIn('manager_agent', call_kwargs)
        self.assertIsNotNone(call_kwargs['manager_agent'])

    @patch('dev_team.crew.Crew')
    @patch('dev_team.crew.Task')
    @patch('dev_team.crew.Agent')
    def test_crew_has_verbose_enabled(self, mock_agent, mock_task, mock_crew):
        """A crew deve ter verbose=True."""
        mock_agent.return_value = MagicMock()
        mock_task.return_value = MagicMock()
        mock_crew.return_value = MagicMock()

        from dev_team.crew import DevTeamCrew
        crew_instance = DevTeamCrew()
        crew_instance.crew()

        call_kwargs = mock_crew.call_args[1]
        self.assertTrue(call_kwargs.get('verbose', False))

    @patch('dev_team.crew.Crew')
    @patch('dev_team.crew.Task')
    @patch('dev_team.crew.Agent')
    def test_crew_has_7_worker_agents(self, mock_agent, mock_task, mock_crew):
        """A crew deve ter 7 agentes trabalhadores (sem o manager)."""
        mock_agent.return_value = MagicMock()
        mock_task.return_value = MagicMock()
        mock_crew.return_value = MagicMock()

        from dev_team.crew import DevTeamCrew
        crew_instance = DevTeamCrew()
        crew_instance.crew()

        call_kwargs = mock_crew.call_args[1]
        agents_list = call_kwargs.get('agents', [])
        self.assertEqual(len(agents_list), 7)


# ══════════════════════════════════════════════════════════════════════════════
# TESTES DE INTEGRAÇÃO — Ambiente e dependências
# ══════════════════════════════════════════════════════════════════════════════
class TestEnvironment(unittest.TestCase):
    """Verifica o ambiente e dependências do projeto."""

    def test_crewai_installed(self):
        """crewai deve estar instalado."""
        try:
            import crewai
        except ImportError:
            self.fail("crewai não está instalado")

    def test_dotenv_installed(self):
        """python-dotenv deve estar instalado."""
        try:
            import dotenv
        except ImportError:
            self.fail("python-dotenv não está instalado")

    def test_yaml_installed(self):
        """pyyaml deve estar instalado."""
        try:
            import yaml
        except ImportError:
            self.fail("pyyaml não está instalado")

    def test_pydantic_installed(self):
        """pydantic deve estar instalado."""
        try:
            import pydantic
        except ImportError:
            self.fail("pydantic não está instalado")

    def test_env_file_exists(self):
        """O arquivo .env deve existir na raiz do projeto."""
        env_path = PROJECT_ROOT / '.env'
        self.assertTrue(env_path.exists(), f".env não encontrado em: {env_path}")

    def test_gemini_api_key_configured(self):
        """GEMINI_API_KEY deve estar configurada no .env."""
        from dotenv import load_dotenv
        env_path = PROJECT_ROOT / '.env'
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
        key = os.getenv('GEMINI_API_KEY')
        self.assertIsNotNone(key, "GEMINI_API_KEY não encontrada no .env")
        self.assertGreater(len(key.strip()), 0, "GEMINI_API_KEY está vazia")

    def test_python_version(self):
        """Python deve ser >= 3.10 e < 3.14."""
        version = sys.version_info
        self.assertGreaterEqual((version.major, version.minor), (3, 10),
                                 f"Python {version.major}.{version.minor} < 3.10")
        self.assertLess((version.major, version.minor), (3, 14),
                        f"Python {version.major}.{version.minor} >= 3.14")

    def test_src_structure(self):
        """A estrutura src/dev_team deve existir."""
        dev_team_path = SRC_PATH / "dev_team"
        self.assertTrue(dev_team_path.exists(), f"Pasta não encontrada: {dev_team_path}")

    def test_config_folder_exists(self):
        """A pasta config deve existir."""
        config_path = SRC_PATH / "dev_team" / "config"
        self.assertTrue(config_path.exists(), f"Pasta config não encontrada: {config_path}")

    def test_prompts_folder_exists(self):
        """A pasta prompts deve existir."""
        prompts_path = SRC_PATH / "dev_team" / "prompts"
        self.assertTrue(prompts_path.exists(), f"Pasta prompts não encontrada: {prompts_path}")


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 70)
    print("  DevTeamCrew — Suite de Testes Completa")
    print("=" * 70)
    print()

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Ordem dos testes
    test_classes = [
        TestEnvironment,
        TestCrewInitialization,
        TestPromptsAndConfigs,
        TestAgentCreation,
        TestTaskCreation,
        TestCrewAssembly,
        TestCrewExecution,
        TestCrewAINative,
    ]

    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 70)
    if result.wasSuccessful():
        print(f"  ✅ TODOS OS TESTES PASSARAM ({result.testsRun} testes)")
    else:
        print(f"  ❌ {len(result.failures)} falha(s), {len(result.errors)} erro(s)")
    print("=" * 70)

    sys.exit(0 if result.wasSuccessful() else 1)