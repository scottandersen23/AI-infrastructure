from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from api.app.config import settings


def configure_tracing() -> trace.Tracer:
    resource = Resource.create(
        {
            "service.name": settings.service_name,
            "deployment.environment": settings.environment,
        }
    )
    provider = TracerProvider(resource=resource)

    if settings.otel_exporter.lower() == "otlp":
        exporter = OTLPSpanExporter(endpoint=settings.otlp_endpoint, insecure=True)
    else:
        exporter = ConsoleSpanExporter()

    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return trace.get_tracer(settings.service_name)


def instrument_fastapi(app) -> None:
    FastAPIInstrumentor.instrument_app(app)


tracer = configure_tracing()
