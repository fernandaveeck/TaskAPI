try:
    from .task_routes import router
except ImportError:
    from routes.task_routes import router

__all__ = ["router"]
