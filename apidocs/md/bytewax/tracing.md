Module bytewax.tracing
======================
Logging and tracing configuration.

Tracing and logging in bytewax are handled in the rust side,
to offer a really detailed view of what is happening in your dataflow.

By default, bytewax sends all "error" logs to the standard output.
This can be configured with the `log_level` parameter of the
`setup_tracing` function.

All the logs emitted by bytewax are structured,
and can be used to setup proper tracing for the dataflow.
To do that you need to talk to a service that collects
and shows data coming from bytewax.

There two possibilities out of the box:
    - Jaeger
    - Opentelemetry collector

### [Openetelemetry Collector](https://opentelemetry.io/docs/collector/)

The Opentelemetry collector is the recommended choice, since it can talk
to a lot of different backends, jaeger included, and you can swap your
tracing infrastructure without touching the dataflow configuration,
since the dataflow only talks to the collector.

### [Jaeger](https://www.jaegertracing.io/)

Bytewax can send traces directly to jaeger, without going through
the opentelemetry collector.
This makes the setup easier, but it's less flexible.

Functions
---------


`setup_tracing(tracing_config=None, log_level=None)`
:   Helper function used to setup tracing and logging from the Rust side.

    Args:
      tracing_config: A subclass of TracingConfig for a specific backend
      log_level: String of the log level, on of ["ERROR", "WARN", "INFO", "DEBUG", "TRACE"]

    By default it starts a tracer that logs all ERROR messages to stdout.

    Note: to make this work, you have to keep a reference of the returned object:

    ```python
    tracer = setup_tracing()
    ```

Classes
-------

`JaegerConfig(service_name, endpoint=None, sampling_ratio=1.0)`
:   Configure tracing to send traces to a Jaeger instance.

    The endpoint can be configured with the parameter passed to this config,
    or with two environment variables:

      OTEL_EXPORTER_JAEGER_AGENT_HOST="127.0.0.1"
      OTEL_EXPORTER_JAEGER_AGENT_PORT="6831"

    By default the endpoint is set to "127.0.0.1:6831".

    If the environment variables are set, the endpoint is changed to that.

    If a config option is passed to JaegerConfig,
    it takes precedence over env vars.

    ### Ancestors (in MRO)

    * bytewax.tracing.TracingConfig

    ### Instance variables

    `sampling_ratio`
    :   Sampling ratio:
        samplig_ratio >= 1 - all traces are sampled
        samplig_ratio <= 0 - most traces are not sampled

`OtlpTracingConfig(service_name, url=None, sampling_ratio=1.0)`
:   Send traces to the opentelemetry collector:
    https://opentelemetry.io/docs/collector/

    Only supports GRPC protocol, so make sure to enable
    it on your OTEL configuration.

    This is the recommended approach since it allows
    the maximum flexibility in what to do with all the data
    bytewax can generate.

    ### Ancestors (in MRO)

    * bytewax.tracing.TracingConfig

    ### Instance variables

    `sampling_ratio`
    :   Sampling ratio:
        samplig_ratio >= 1 - all traces are sampled
        samplig_ratio <= 0 - most traces are not sampled

    `service_name`
    :   Service name, identifies this dataflow.

    `url`
    :   Optional collector's URL, defaults to `grpc:://127.0.0.1:4317`

`TracingConfig()`
:   Base class for tracing/logging configuration.

    There defines what to do with traces and logs emitted by Bytewax.

    Use a specific subclass of this to configure where you want the
    traces to go.

    ### Descendants

    * bytewax.tracing.JaegerConfig
    * bytewax.tracing.OtlpTracingConfig
