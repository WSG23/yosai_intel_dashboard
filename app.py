"""Entry point for the Yōsai Intel Dashboard."""
from core.app_factory import create_app


if __name__ == "__main__":
    dashboard = create_app()
    dashboard.run()
