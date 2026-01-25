from langchain.chat_models import init_chat_model
import importlib.util
from pathlib import Path

# Load project settings directly from file to avoid name conflicts with installed
# packages named `config` in the environment.
settings_path = Path(__file__).resolve().parents[1] / "config" / "settings.py"
spec = importlib.util.spec_from_file_location("project_config", str(settings_path))
project_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(project_config)
settings = project_config.settings


# Initialize LLM instances using local project settings. If initialization fails
# (missing API keys or provider libraries), fall back to a lightweight mock
# implementation so the app can be tested locally without external credentials.
try:
	router_llm = init_chat_model(f"openai:{settings.ROUTER_MODEL}")
	agent_llm = init_chat_model(f"openai:{settings.AGENT_MODEL}")
except Exception:
	class _MockRouter:
		def with_structured_output(self, schema):
			return self

		def invoke(self, messages):
			# Simple heuristic-based mock for classification and synthesis
			user_text = ""
			sys_text = ""
			for m in messages:
				if m.get("role") == "user":
					user_text = m.get("content", "")
				if m.get("role") == "system":
					sys_text = m.get("content", "")

			if "determine which knowledge bases" in sys_text.lower() or "available sources" in sys_text.lower():
				classifications = []
				q = user_text or ""
				if any(tok in q.lower() for tok in ("auth", "authenticate", "authentication", "jwt")):
					classifications.append({"source": "github", "query": "What authentication code exists? Search for auth middleware, JWT handling"})
					classifications.append({"source": "notion", "query": "What authentication documentation exists? Look for API auth guides"})
				else:
					classifications.append({"source": "github", "query": q})
				return type("R", (), {"classifications": classifications})

			# Synthesis fallback: return a concatenated summary string
			for m in messages:
				if m.get("role") == "user":
					combined = m.get("content", "")
					return f"SYNTHESIZED ANSWER:\n{combined}"

	router_llm = _MockRouter()
	agent_llm = _MockRouter()