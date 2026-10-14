FROM ghcr.io/astral-sh/uv:0.11.0 AS uv
FROM python:3.13-slim
COPY --from=uv /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock .python-version ./
COPY src/ src/
RUN uv sync --locked --no-dev
COPY config/ config/
COPY prompts/ prompts/
COPY data/ data/
COPY evaluation/ evaluation/
RUN useradd --create-home agent && mkdir logs traces reports state && chown -R agent:agent /app
USER agent
ENTRYPOINT ["uv", "run", "--no-sync", "salesops-agent"]
CMD ["--help"]
