import pytest

pytest.importorskip("yaml")
pytest.importorskip("dash")
pytest.importorskip("dash_bootstrap_components")

from core.app_factory import create_app


def test_create_app_instance():
    app = create_app()
    assert app is not None
    assert hasattr(app, "layout")
    assert app.title == "Yōsai Intel Dashboard"

