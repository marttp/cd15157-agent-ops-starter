import hashlib
import os
import subprocess
from pathlib import Path

import yaml
from dotenv import load_dotenv
from pydantic import Field

from .schemas import Contract


class Settings(Contract):
    version: str
    model: str
    provider: str = "vocareum"
    temperature: float = Field(ge=0, le=2)
    request_timeout_s: float = Field(gt=0, le=120)
    max_model_calls: int = Field(ge=1, le=20)
    reference_date: str
    prompt: str
    data_dir: str
    output_dir: str
    input_usd_per_million: float = Field(ge=0)
    output_usd_per_million: float = Field(ge=0)
    price_version: str


def load_settings(path=None):
    path = Path(path or "config/agent_v1.yaml").resolve()
    cfg = Settings.model_validate(yaml.safe_load(path.read_text()))
    root = path.parent.parent
    load_dotenv(root / ".env", override=False)
    return cfg, root


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def metadata(cfg, root):
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                            capture_output=True, text=True).stdout.strip() or "unknown"
    return {"git_commit": commit, "config_version": cfg.version,
            "config_sha256": digest(root / "config/agent_v1.yaml"),
            "prompt_sha256": digest(root / cfg.prompt), "prompt_version": "system-v1",
            "effective_config": cfg.model_dump(), "schema_version": "schemas-v1", "tool_version": "tools-v1",
            "dataset_sha256": {p.name: digest(p) for p in sorted((root / cfg.data_dir).glob("*.json"))},
            "provider": os.getenv("LLM_PROVIDER", cfg.provider), "model": cfg.model,
            "reference_date": cfg.reference_date, "price_version": cfg.price_version}


def make_model(cfg):
    from langchain_openai import ChatOpenAI
    provider = os.getenv("LLM_PROVIDER", cfg.provider)
    if provider not in {"vocareum", "openai"}:
        raise ValueError("unsupported_provider")
    key = os.getenv("VOCAREUM_API_KEY" if provider == "vocareum" else "OPENAI_API_KEY")
    if not key:
        raise RuntimeError("provider_credentials_missing")
    kwargs = {"base_url": "https://openai.vocareum.com/v1"} if provider == "vocareum" else {}
    return ChatOpenAI(model=cfg.model, api_key=key, temperature=cfg.temperature,
                      timeout=cfg.request_timeout_s, max_retries=0, **kwargs)
