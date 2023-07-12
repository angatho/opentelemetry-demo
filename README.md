# Opentelemetry Python Demo 
## Introduction
This is an opentelemetry demo built in python focused on capturing traces, metrics, and logs and sending them to Dynatrace based on the example present here
https://www.dynatrace.com/support/help/extend-dynatrace/opentelemetry/walkthroughs/python

This demo has been fully instrumented to include two endpoints (/ and /parent) via flask to demonstrate:
* Trace ingestion
  * Single endpoint
  * Parent/child spans
  * Child span that is a method with no endpoint
* Metric ingestion
  * Request counter
  * Metric attributes for filter and split by in Dynatrace
* Log ingestion
  * Linking opentelemetry logs to traces in Dynatrace

At the time this was written the opentelemetry status for logs in python was experimental so the method to use OpenTelemetry to capture logs may change.

## How to use

1. Ensure python is installed on your machine
2. Ensure that all the dependences required are installed
3. Modify the DT_API_URL with your endpoint, and add your API token that has the following [scopes](https://www.dynatrace.com/support/help/shortlink/otel-getstarted-otlpexport#authentication-export-to-activegate)
4. Run the python script. When running this demo app, flask will run on port 5000. So you can access this on your local machine via localhost:5000, to access the parent endpoint use localhost:5000/parent

## Breakdown of how each OpenTelemetry signal is captured
* This app will send traces to Dynatrace based on the endpoint that is accessed, there is wait time added to each endpoint to simulate reponse times
![image](https://github.com/angatho/opentelemetry-demo/assets/43062498/f75ca119-3992-4ca4-843a-efd6ac3738f8)

* A metric counting the number of requests will also be sent and this will include the endpoint data so you can differentiate with how many times each endpoint is accessed
![image](https://github.com/angatho/opentelemetry-demo/assets/43062498/0c351cb6-c681-4911-a3ca-4ab8a2dfdeef)

* Only logs that are error status and above will be ingested, ingested logs will be linked to their respective traces.
![image](https://github.com/angatho/opentelemetry-demo/assets/43062498/ef8f92e3-6fd4-4af6-a9b0-ceae4f885363)
![image](https://github.com/angatho/opentelemetry-demo/assets/43062498/e5eab27e-0996-4cdb-a905-a07d1a43ffce)

