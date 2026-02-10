import logging
import sys

import structlog
from opentelemetry import trace

from .config import settings


def _add_trace_context(
    _logger: structlog.stdlib.BoundLogger,
    _method_name: str,
    event_dict: dict[str, object],
) -> dict[str, object]:
    """Attach OpenTelemetry trace/span ids to log record if span is active."""
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if ctx and ctx.is_valid:
        event_dict["trace_id"] = trace.format_trace_id(ctx.trace_id)
        event_dict["span_id"] = trace.format_span_id(ctx.span_id)
    
    event_dict.setdefault("service_name", settings.APP_NAME)
    return event_dict


def _extract_stdlib_args(
    _logger: structlog.stdlib.BoundLogger,
    _method_name: str,
    event_dict: dict[str, object],
) -> dict[str, object]:
    """Extract args from stdlib record to positional_args for structlog."""
    if "args" in event_dict:
        event_dict["positional_args"] = event_dict.pop("args")
    return event_dict


def configure_logging() -> None:
    """Configure stdlib logging and structlog for JSON output."""
    
    # Processors that are safe to run in both structlog and stdlib formatter (foreign_pre_chain)
    # filter_by_level is NOT safe for stdlib formatter as logger is None there
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        _add_trace_context,
        structlog.processors.EventRenamer("msg"),
    ]

    # Structlog configuration
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level, # Filter by level is safe here
        ] + shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Stdlib formatter that renders as JSON
    formatter = structlog.stdlib.ProcessorFormatter(
        # These run on logs NOT from structlog (e.g. uvicorn)
        foreign_pre_chain=shared_processors,
        # These run on ALL logs (after structlog processors or foreign_pre_chain)
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Configure Root Logger
    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(settings.LOG_LEVEL.upper())

    # Configure Uvicorn Loggers
    # We replace handlers to ensure they use our JSON formatter
    for _log in ["uvicorn", "uvicorn.error"]:
        logger = logging.getLogger(_log)
        logger.handlers = [handler]
        logger.propagate = False
    
    # Silence uvicorn.access as it is redundant with middleware logging and hard to format as JSON
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.access").propagate = False


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a configured structlog logger."""
    if name is None:
        return structlog.get_logger()
    return structlog.get_logger(name)
