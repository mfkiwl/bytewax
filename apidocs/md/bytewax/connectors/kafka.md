Module bytewax.connectors.kafka
===============================
Connectors for [Kafka](https://kafka.apache.org).

Importing this module requires the
[`confluent-kafka`](https://github.com/confluentinc/confluent-kafka-python)
package to be installed.

Classes
-------

`KafkaSink(brokers: Iterable[str], topic: str, add_config: Dict[str, str] = None)`
:   Use a single Kafka topic as an output sink.

    Items consumed from the dataflow must look like two-tuples of
    `(key_bytes, value_bytes)`. Default partition routing is used.

    Workers are the unit of parallelism.

    Can support at-least-once processing. Messages from the resume
    epoch will be duplicated right after resume.

    Init.

    Args:
        brokers:
            List of `host:port` strings of Kafka brokers.
        topic:
            Topic to produce to.
        add_config:
            Any additional configuration properties. See [the
            `rdkafka`
            documentation](https://github.com/confluentinc/librdkafka/blob/master/CONFIGURATION.md)
            for options.

    ### Ancestors (in MRO)

    * bytewax.outputs.DynamicSink
    * bytewax.outputs.Sink
    * abc.ABC

    ### Methods

    `build(self, worker_index, worker_count)`
    :   See ABC docstring.

`KafkaSource(brokers: Iterable[str], topics: Iterable[str], tail: bool = True, starting_offset: int = -2, add_config: Dict[str, str] = None, batch_size: int = 1)`
:   Use a set of Kafka topics as an input source.

    Kafka messages are emitted into the dataflow as two-tuples of
    `(key_bytes, value_bytes)`.

    Partitions are the unit of parallelism.

    Can support exactly-once processing.

    Init.

    Args:
        brokers:
            List of `host:port` strings of Kafka brokers.
        topics:
            List of topics to consume from.
        tail:
            Whether to wait for new data on this topic when the
            end is initially reached.
        starting_offset:
            Can be either `confluent_kafka.OFFSET_BEGINNING` or
            `confluent_kafka.OFFSET_END`. Defaults to beginning of
            topic.
        add_config:
            Any additional configuration properties. See [the
            `rdkafka`
            documentation](https://github.com/confluentinc/librdkafka/blob/master/CONFIGURATION.md)
            for options.
        batch_size:
            How many messages to consume at most at each poll.
            This is 1 by default, which means messages will be
            consumed one at a time. The default setting is suited
            for lower latency, but negatively affects
            throughput. If you need higher throughput, set this to
            a higher value (eg: 1000)

    ### Ancestors (in MRO)

    * bytewax.inputs.FixedPartitionedSource
    * bytewax.inputs.Source
    * abc.ABC

    ### Methods

    `build_part(self, _now: datetime.datetime, for_part: str, resume_state: Optional[Any])`
    :   See ABC docstring.

    `list_parts(self)`
    :   Each Kafka partition is an input partition.
