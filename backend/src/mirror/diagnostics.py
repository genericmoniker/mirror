import asyncio
import logging
from io import StringIO

_logger = logging.getLogger(__name__)


def log_task_stacks():
    file = StringIO()
    print("Dumping tasks", file=file)
    for task in asyncio.all_tasks():
        task.print_stack(file=file)
        print(file=file)
    _logger.info(file.getvalue())
