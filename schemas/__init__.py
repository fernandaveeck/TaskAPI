try:
    from .task_schemas import Task, TaskCreate, TaskUpdate
except ImportError:
    from schemas.task_schemas import Task, TaskCreate, TaskUpdate

__all__ = ["Task", "TaskCreate", "TaskUpdate"]
