# Mirror — Agent Instructions

Smart Mirror dashboard for Raspberry Pi. Python/Starlette backend, HTMX + SSE frontend, Jinja2 templates, plugin-based widget system.

## Build & Test

```bash
uv sync                                    # Install all dependencies
uv run python src/mirror/main.py           # Start dev server (localhost:5000)
uv run pytest                              # Run all tests
uv run pytest -k <name>                    # Filter tests by name
```

Type checking: `mypy` (configured in [mypy.ini](mypy.ini)). Linting: `ruff` (configured in [pyproject.toml](pyproject.toml)).

## Architecture

- **[src/mirror/main.py](src/mirror/main.py)** — Starlette app, routes, startup/shutdown
- **[src/mirror/plugin_manager.py](src/mirror/plugin_manager.py)** — loads, renders, and manages plugins
- **[src/mirror/event_bus.py](src/mirror/event_bus.py)** — SSE broadcast; plugins call `context.widget_updated(data)` to push updates
- **[src/mirror/plugin_context.py](src/mirror/plugin_context.py)** — `PluginContext` injected into plugins: config, encrypted DB, `widget_updated()`
- **[src/mirror/layout.py](src/mirror/layout.py)** — reads `instance/mirror.toml` layout section
- **[instance/mirror.toml](instance/mirror.toml)** — runtime layout + per-plugin config (not committed with secrets)

**Data flow**: plugin async task fetches data → calls `context.widget_updated(data)` → EventBus broadcasts SSE event → browser HTMX-swaps the widget HTML.

## Plugin Conventions

Each plugin is a **namespace package** under `src/mirror/plugins/<name>/`:

```
my_plugin/
├─ __init__.py       # Re-exports hook functions (required)
├─ my_plugin.html    # Jinja2 widget template (required)
└─ static/           # CSS/JS/assets (optional; served at /plugin/<name>/)
```

Optional hook functions exported from `__init__.py`:
- `start_plugin(context: PluginContext)` — launch background async task
- `stop_plugin(context: PluginContext)` — cancel tasks
- `set_authorization_code(plugin_context, code, state)` — OAuth callback

**Multi-widget plugins** (e.g., `calendars`): widget name is `<plugin>-<widget>` in layout config (e.g., `calendars-agenda`). Pass `widget_name=` to `context.widget_updated()`. Template filename matches widget name: `agenda.html`.

## Frontend Conventions

- **SSE event names**: `{plugin_name}.refresh` or `{plugin_name}-{widget_name}.refresh`
- **CSS scoping**: prefix all selectors with `#{plugin_name}` to avoid conflicts
- **`url_for(filename)`**: available in plugin templates, resolves to `/plugin/<name>/<filename>`
- **Static JS/CSS**: listed via `Plugin.scripts` / `Plugin.stylesheets` properties if needed globally

## Testing Patterns

- Tests live in [tests/mirrortests/](tests/mirrortests/)
- All tests are `async def` — `asyncio_mode = "auto"` in pytest config
- Use [tests/mirrortests/doubles/plugin_context.py](tests/mirrortests/doubles/plugin_context.py) as the mock `PluginContext`; it collects updates in `context.update` instead of broadcasting via SSE. Set `context.config` (dict) and `context.db` (dict) directly in tests.
- Inject a fake data-fetcher function to avoid real network calls; see [tests/mirrortests/plugins/calendars/](tests/mirrortests/plugins/calendars/) for examples

## Configuration & Paths

- `instance/` is the runtime data directory: `mirror.toml`, `mirror.db` (encrypted), `mirror.key`, OAuth secrets
- [src/mirror/paths.py](src/mirror/paths.py) defines `ROOT_DIR` and `INSTANCE_DIR`
- Plugin config is accessed via `context.config` (dict keyed from `[plugin.<name>]` in `mirror.toml`)
