import json
import logging
import time

from flask import Flask
from opentelemetry import metrics, trace
from opentelemetry.sdk.resources import Resource

# Import exporters
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

# Trace imports
from opentelemetry.trace import set_tracer_provider, get_tracer_provider, SpanKind
from opentelemetry.sdk.trace import TracerProvider, sampling
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Metric imports
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.metrics import MeterProvider, Counter, UpDownCounter, Histogram, ObservableCounter, ObservableUpDownCounter
from opentelemetry.metrics import set_meter_provider, get_meter_provider

# Logs import
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

# ===== GENERAL SETUP =====

DT_API_URL = "https://environmentid.dynatrace.com/api/v2/otlp"
DT_API_TOKEN = ""


merged = dict()
for name in ["dt_metadata_e617c525669e072eebe3d0f08212e8f2.json", "/var/lib/dynatrace/enrichment/dt_metadata.json"]:
  try:
    data = ''
    with open(name) as f:
      data = json.load(f if name.startswith("/var") else open(f.read()))
      merged.update(data)
  except:
    pass

merged.update({
  "service.name": "otel-demo", 
  "service.version": "1.0.1", 
})
resource = Resource.create(merged)


# ===== TRACING SETUP =====

tracer_provider = TracerProvider(sampler=sampling.ALWAYS_ON, resource=resource)
set_tracer_provider(tracer_provider)

tracer_provider.add_span_processor(
  BatchSpanProcessor(
    OTLPSpanExporter(
      endpoint = DT_API_URL + "/v1/traces",
      headers = {
        "Authorization": "Api-Token " + DT_API_TOKEN
      }
    )
  )
)

tracer = get_tracer_provider().get_tracer(__name__)


# ===== METRIC SETUP =====

exporter = OTLPMetricExporter(
  endpoint = DT_API_URL + "/v1/metrics",
  headers = {"Authorization": "Api-Token " + DT_API_TOKEN},
  preferred_temporality = {
    Counter: AggregationTemporality.DELTA,
    UpDownCounter: AggregationTemporality.CUMULATIVE,
    Histogram: AggregationTemporality.DELTA,
    ObservableCounter: AggregationTemporality.DELTA,
    ObservableUpDownCounter: AggregationTemporality.CUMULATIVE,
  }
)

reader = PeriodicExportingMetricReader(exporter=exporter)
meter_provider = MeterProvider(metric_readers=[reader], resource=resource)

meter = meter_provider.get_meter(__name__)

# Create request count metric 
request_counter = meter.create_counter(
  name="requests",
  description="The number of requests received"
)

# ===== LOG SETUP =====

logger_provider = LoggerProvider(resource=resource)

logger_provider.add_log_record_processor(
  BatchLogRecordProcessor(OTLPLogExporter(
    endpoint = DT_API_URL + "/v1/logs",
	headers = {"Authorization": "Api-Token " + DT_API_TOKEN}
  ))
)
handler = LoggingHandler(level=logging.ERROR, logger_provider=logger_provider)

# Attach OTLP handler to root logger
logging.getLogger().addHandler(handler)

# Start flask
app = Flask(__name__)

@app.route("/")
def index():
    # Generate span
    with tracer.start_as_current_span("Call to /", kind=SpanKind.SERVER) as index:

      index.set_attribute("http.method", "GET")
      index.set_attribute("span.kind", "server")
      # Generate metric
      request_counter.add(1, {"Endpoint":"/"})
      # Generate a log entry
      logging.info("Index endpoint called")
      logging.warning("Index endpoint called")
      logging.error("Index endpoint called")      
      time.sleep(0.15)

      return "Index"

@app.route("/parent")
def parentchild():
    # Generate span
    with tracer.start_as_current_span("Call to /parent", kind=SpanKind.SERVER) as parent:

      parent.set_attribute("http.method", "GET")
      parent.set_attribute("span.kind", "server")
      # Generate metric
      request_counter.add(1, {"Endpoint":"/parent"})
      # Generate log entry
      logging.info("Parent endpoint called")
      logging.warning("Parent endpoint called")
      logging.error("Parent endpoint called")
      time.sleep(0.5)
      child()
    
      return "Parent child span"

def child():
    # Start a new span as a child of the current span
    with tracer.start_as_current_span("child") as child:
      # Generate log entry
      logging.info("Child method called")
      logging.warning("Child method called")
      logging.error("Child method called")
      time.sleep(1)
      
      return "child"

if __name__ == "__main__":
  app.run(host='0.0.0.0', port='5000')

