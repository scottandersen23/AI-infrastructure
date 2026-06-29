from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

from executor.app.config import settings


def configure_tracing() -> None:
    if not settings.otel_exporter or settings.otel_exporter.lower() == "none":
        return

    provider = TracerProvider(
        resource=Resource.create(
            {
                "service.name": settings.service_name,
                "deployment.environment": settings.environment,
            }
        )
    )

    if settings.otel_exporter.lower() == "console":
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)


tracer = trace.get_tracer(settings.service_name)
