import os

from openinference.instrumentation.google_adk import GoogleADKInstrumentor
from phoenix.otel import register

from repo_stargazer import Settings


def enable_arize_otel_if_needed(settings: Settings) -> None:
    if settings.phoenix_otel:
        os.environ["PHOENIX_API_KEY"] = settings.phoenix_otel.api_key.get_secret_value()

        tracer_provider = register(
            endpoint=settings.phoenix_otel.collection_endpoint,
            project_name=settings.phoenix_otel.project_name,
            auto_instrument=True,
        )
        GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)
