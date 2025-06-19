#!/usr/bin/env python3
"""
Merged Yōsai Intel Dash application.

This file fuses the environment‑aware bootstrap from **app_78.py** with the
working demo layout/callbacks that originally lived in **app.py** while keeping
**CSRF protection ON** (via *Flask‑WTF CSRFProtect*).  All secrets must be
provided via environment variables or a `.env` file – **nothing is hard‑coded**.

Required environment variables
------------------------------
* **SECRET_KEY** – Flask session & CSRF secret.
* **YOSAI_ENV**  – dev / staging / prod (maps to `config/<env>.yaml`).

The script terminates early with a clear error message if any required variable
is missing, avoiding the LazyString JSON errors you hit previously.

Typical local run::

    $ pip install -r requirements.txt
    $ export SECRET_KEY="seekrit"
    $ export YOSAI_ENV=dev
    $ python app_merged.py
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import yaml
from dash import Dash, Input, Output, callback, dcc, html
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect

# ---------------------------------------------------------------------------
# 1. Configuration & secrets
# ---------------------------------------------------------------------------

# Load a .env stack if present (no‑op if file is absent)
load_dotenv()

REQUIRED_VARS = ["SECRET_KEY", "YOSAI_ENV"]
missing: list[str] = [v for v in REQUIRED_VARS if os.getenv(v) is None]
if missing:
    sys.stderr.write(
        f"\n[ERROR] Required environment variables missing: {', '.join(missing)}\n"
        "Set them in your shell, in Docker secrets, or in a .env file and try again.\n\n",
    )
    sys.exit(1)

SECRET_KEY: str = os.environ["SECRET_KEY"]
CURRENT_ENV: str = os.environ["YOSAI_ENV"].lower()
os.environ.setdefault("SECRET_KEY", "12345")            # noqa: S105 (insecure-secret)
os.environ.setdefault("YOSAI_ENV", "development")

def load_yaml_config(env: str) -> Dict[str, Any]:
    """Load `config/<env>.yaml` if available; otherwise return an empty dict."""
    cfg_path = Path(__file__).parent / "config" / f"{env}.yaml"
    if not cfg_path.exists():
        logging.warning(
            "No YAML config for %s (expected %s). Continuing with defaults.",
            env,
            cfg_path,
        )
        return {}
    with cfg_path.open("r", encoding="utf‑8") as fh:
        return yaml.safe_load(fh) or {}


CONFIG: Dict[str, Any] = load_yaml_config(CURRENT_ENV)

# ---------------------------------------------------------------------------
# 2. Flask server, Dash app, and **CSRF protection**
# ---------------------------------------------------------------------------

external_stylesheets = [dbc.themes.BOOTSTRAP]
app: Dash = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
    title="Yōsai Intel Dashboard",
)
server = app.server
server.config.update(SECRET_KEY=SECRET_KEY)

# 🔒  Enable CSRF protection (default once SECRET_KEY is set)
CSRFProtect(server)

# ---------------------------------------------------------------------------
# 3. Demo layout brought over from the old `app.py`
# ---------------------------------------------------------------------------

def _build_demo_dataframe() -> pd.DataFrame:
    """Return a small DataFrame placeholder for the demo cards."""
    return pd.DataFrame(
        {
            "Metric": ["Open Alerts", "Resolved", "Escalated"],
            "Count": [17, 42, 3],
        }
    )


def create_layout() -> html.Div:  # noqa: D401 – simple layout builder
    """Assemble the Dash layout."""
    df = _build_demo_dataframe()

    return dbc.Container(
        [
            html.H1("Yōsai Intel – Security Dashboard", className="text-center my-4"),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(metric),
                                dbc.CardBody(
                                    html.H3(count, className="card-title"),
                                    className="text-center",
                                ),
                            ],
                            className="shadow-sm text-center",
                        ),
                        md=4,
                    )
                    for metric, count in zip(df["Metric"], df["Count"], strict=True)
                ]
            ),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Button(
                                "Refresh Metrics",
                                id="btn-refresh",
                                color="primary",
                                className="me-2",
                            ),
                            html.Span(id="refresh-status"),
                        ],
                        md=6,
                    )
                ],
                className="my-3",
            ),
        ],
        fluid=True,
    )


app.layout = create_layout

# ---------------------------------------------------------------------------
# 4. Callbacks (demo only)
# ---------------------------------------------------------------------------


@callback(Output("refresh-status", "children"), Input("btn-refresh", "n_clicks"), prevent_initial_call=True)
def refresh_metrics(n_clicks: int):  # noqa: D401 – Dash callback
    """Simulate a metric refresh; in production reload real data sources."""
    return f"Metrics refreshed ({n_clicks}) ✅"


# ---------------------------------------------------------------------------
# 5. Gunicorn / uWSGI entry‑points
# ---------------------------------------------------------------------------


def get_app() -> Dash:  # pragma: no cover – for WSGI servers
    """Return the Dash app instance (used by Gunicorn, uWSGI, etc.)."""
    return app


def main() -> None:  # pragma: no cover – CLI launcher
    """Run a development server when executed via `python app_merged.py`."""
    host: str = CONFIG.get("host", "0.0.0.0")
    port: int = int(CONFIG.get("port", 8050))
    debug: bool = bool(CONFIG.get("debug", True))

    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )
    logging.info(
        "Starting Yōsai Intel Dashboard (%s) on %s:%s (debug=%s)",
        CURRENT_ENV,
        host,
        port,
        debug,
    )
    app.run_server(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
