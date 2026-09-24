"""Skill vocabulary used to read both your resume and job descriptions.

Each canonical skill maps to regex aliases. Add to this if your resume has
skills that aren't being picked up (run `python -m jobcollector skills`).
"""
from __future__ import annotations

import re

SKILLS: dict[str, list[str]] = {
    # Languages
    "Python": [r"python"],
    "TypeScript": [r"typescript", r"\bts\b"],
    "JavaScript": [r"javascript", r"\bjs\b"],
    "Java": [r"\bjava\b"],
    "Go": [r"\bgolang\b", r"\bgo\b(?= (?:lang|developer|engineer|services?|microservices))"],
    "Rust": [r"\brust\b"],
    "C++": [r"c\+\+"],
    "SQL": [r"\bsql\b"],
    "Bash": [r"\bbash\b", r"shell scripting"],
    # Backend / web
    "Node.js": [r"node\.?js", r"\bnode\b"],
    "FastAPI": [r"fastapi"],
    "Flask": [r"\bflask\b"],
    "Django": [r"django"],
    "React": [r"\breact(?:\.js)?\b"],
    "Next.js": [r"next\.?js"],
    "REST APIs": [r"\brest(?:ful)?\b", r"rest api"],
    "GraphQL": [r"graphql"],
    "gRPC": [r"\bgrpc\b"],
    "Microservices": [r"microservices?"],
    # Data stores
    "PostgreSQL": [r"postgres(?:ql)?"],
    "MySQL": [r"mysql"],
    "MongoDB": [r"mongo(?:db)?"],
    "Redis": [r"\bredis\b"],
    "Supabase": [r"supabase"],
    "Elasticsearch": [r"elastic ?search", r"opensearch"],
    "Snowflake": [r"snowflake"],
    "BigQuery": [r"bigquery"],
    # LLM / GenAI
    "LLMs": [r"\bllms?\b", r"large language models?"],
    "Generative AI": [r"generative ai", r"\bgen ?ai\b"],
    "RAG": [r"\brag\b", r"retrieval[- ]augmented"],
    "Prompt Engineering": [r"prompt engineering", r"prompt design"],
    "AI Agents": [r"\bagents?\b", r"agentic", r"multi-agent"],
    "Tool Use / Function Calling": [r"tool use", r"tool calling", r"function calling"],
    "LLM Evaluation": [r"\bevals?\b", r"llm evaluation", r"evaluation harness", r"model evaluation"],
    "Fine-tuning": [r"fine-?tun(?:e|ing)", r"\blora\b", r"\bpeft\b", r"\brlhf\b", r"\bsft\b"],
    "Embeddings": [r"embeddings?"],
    "Vector Databases": [r"vector (?:db|database|store|search)s?"],
    "OpenAI API": [r"openai", r"\bgpt-?\d"],
    "Anthropic / Claude": [r"anthropic", r"\bclaude\b"],
    "LangChain": [r"langchain"],
    "LangGraph": [r"langgraph"],
    "LlamaIndex": [r"llama ?index"],
    "Pinecone": [r"pinecone"],
    "Weaviate": [r"weaviate"],
    "pgvector": [r"pgvector"],
    "Hugging Face": [r"hugging ?face", r"transformers library"],
    "Guardrails": [r"guardrails?"],
    "Structured Outputs": [r"structured outputs?", r"json schema", r"json mode"],
    "MCP": [r"model context protocol", r"\bmcp\b"],
    "Computer Vision": [r"computer vision", r"\bocr\b", r"vision models?"],
    "NLP": [r"\bnlp\b", r"natural language processing"],
    # ML
    "Machine Learning": [r"machine learning", r"\bml\b"],
    "Deep Learning": [r"deep learning", r"neural networks?"],
    "PyTorch": [r"pytorch", r"\btorch\b"],
    "TensorFlow": [r"tensorflow", r"\bkeras\b"],
    "scikit-learn": [r"scikit-?learn", r"sklearn"],
    "Pandas": [r"\bpandas\b"],
    "NumPy": [r"numpy"],
    "MLOps": [r"mlops", r"model deployment", r"model serving"],
    "MLflow": [r"mlflow"],
    "Spark": [r"\bspark\b", r"pyspark"],
    "Airflow": [r"airflow"],
    "Kafka": [r"kafka"],
    "ETL / Data Pipelines": [r"\betl\b", r"data pipelines?"],
    # Infra
    "AWS": [r"\baws\b", r"amazon web services", r"\bec2\b", r"\bs3\b", r"lambda", r"sagemaker", r"bedrock"],
    "GCP": [r"\bgcp\b", r"google cloud", r"vertex ai"],
    "Azure": [r"azure"],
    "Docker": [r"docker", r"containeri[sz]"],
    "Kubernetes": [r"kubernetes", r"\bk8s\b"],
    "Terraform": [r"terraform"],
    "CI/CD": [r"ci/cd", r"github actions", r"\bjenkins\b", r"continuous integration"],
    "Linux": [r"\blinux\b"],
    "Git": [r"\bgit\b"],
    # Automation / scraping
    "Playwright": [r"playwright"],
    "Selenium": [r"selenium"],
    "Web Scraping": [r"web scraping", r"scrap(?:er|ing)"],
    "n8n": [r"\bn8n\b"],
    "Workflow Automation": [r"workflow automation", r"zapier", r"\bn8n\b"],
    "Webhooks": [r"webhooks?"],
    "OAuth": [r"oauth ?2?", r"\bsso\b", r"\boidc\b"],
    "Stripe API": [r"stripe (?:api|integration|payments)"],
    # Practices
    "System Design": [r"system design", r"distributed systems"],
    "Multi-tenancy": [r"multi-?tenan(?:t|cy)"],
    "Observability": [r"observability", r"monitoring", r"datadog", r"prometheus", r"grafana"],
    "Testing": [r"unit tests?", r"pytest", r"\bjest\b", r"test automation"],
}

_COMPILED = {name: re.compile("|".join(f"(?:{a})" for a in aliases), re.I)
             for name, aliases in SKILLS.items()}


def extract_skills(text: str) -> set[str]:
    return {name for name, rx in _COMPILED.items() if rx.search(text)}
