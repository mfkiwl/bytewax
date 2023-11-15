Module bytewax.outputs
======================
Low-level output interfaces.

If you want pre-built connectors for various external systems, see
`bytewax.connectors`. That is also a rich source of examples.

Subclass the types here to implement output for your own custom sink.

Classes
-------

`DynamicSink()`
:   An output sink where all workers write items concurrently.

    Does not support storing any resume state. Thus these kind of
    outputs only naively can support at-least-once processing.

    ### Ancestors (in MRO)

    * bytewax.outputs.Sink
    * abc.ABC

    ### Descendants

    * bytewax.connectors.kafka.KafkaSink
    * bytewax.connectors.stdio.StdOutSink
    * bytewax.testing.TestingSink

    ### Methods

    `build(self, worker_index, worker_count) ‑> bytewax.outputs.StatelessSinkPartition`
    :   Build an output partition for a worker.

        Will be called once on each worker.

        Args:
            worker_index:
                Index of this worker.
            worker_count:
                Total number of workers.

        Returns:
            The built partition.

`FixedPartitionedSink()`
:   An output sink with a fixed number of independent partitions.

    Will maintain the state of each partition and re-build using it during
    resume. If the sink supports seeking and overwriting, this output
    can support exactly-once processing.

    ### Ancestors (in MRO)

    * bytewax.outputs.Sink
    * abc.ABC

    ### Descendants

    * bytewax.connectors.files.DirSink
    * bytewax.connectors.files.FileSink

    ### Methods

    `build_part(self, for_part: str, resume_state: Optional[Any]) ‑> bytewax.outputs.StatefulSinkPartition`
    :   Build anew or resume an output partition.

        Will be called once per execution for each partition key on a
        worker that reported that partition was local in `list_parts`.

        Do not pre-build state about a partition in the
        constructor. All state must be derived from `resume_state` for
        recovery to work properly.

        Args:
            for_part:
                Which partition to build. Will always be one of the
                keys returned by `list_parts` on this worker.

            resume_state:
                State data containing where in the output stream this
                partition should be begin writing during this
                execution.

        Returns:
            The built partition.

    `list_parts(self) ‑> List[str]`
    :   List all local partitions this worker has access to.

        You do not need to list all partitions globally.

        Returns:
            Local partition keys.

    `part_fn(self, item_key: str) ‑> int`
    :   Route incoming `(key, value)` pairs to partitions.

        Defaults to `zlib.adler32` as a simple consistent function.

        This must be globally consistent across workers and executions
        and return the same hash on every call.

        A specific partition is chosen by wrapped indexing this value
        into the ordered global set of partitions. (Not just
        partitions local to this worker.)

        .. caution:: Do not use Python's built in `hash` function
            here! It is [_not consistent between processes by
            default_](https://docs.python.org/3/using/cmdline.html#cmdoption-R)
            and using it will cause incorrect partitioning in cluster
            executions.

        Args:
            item_key:
                Key for the value that is about to be written.

        Returns:
            Integer hash value that is used to assign partition.

`Sink()`
:   A destination to write output items.

    Base class for all output sinks. Do not subclass this.

    If you want to implement a custom connector, instead subclass one
    of the specific sink sub-types below in this module.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * bytewax.outputs.DynamicSink
    * bytewax.outputs.FixedPartitionedSink

`StatefulSinkPartition()`
:   Output partition that maintains state of its position.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * bytewax.connectors.files._FileSinkPartition

    ### Methods

    `close(self) ‑> None`
    :   Cleanup this partition when the dataflow completes.

        This is not guaranteed to be called. It will only be called
        when the dataflow finishes on finite input. It will not be
        called during an abrupt or abort shutdown.

    `snapshot(self) ‑> Any`
    :   Snapshot the position of the next write of this partition.

        This will be returned to you via the `resume_state` parameter
        of your output builder.

        Be careful of "off by one" errors in resume state. This should
        return a state that, when built into a partition, resumes writing
        _after the last written item_, not overwriting the same item.

        This is guaranteed to never be called after `close()`.

        Returns:
            Resume state.

    `write_batch(self, values: List[Any]) ‑> None`
    :   Write a batch of output values.

        Called with a list of `value`s for each `(key, value)` at this
        point in the dataflow.

        See `PartitionedOutput.part_fn` for how the key is mapped to
        partition.

        Args:
            values:
                Values in the dataflow. Non-deterministically batched.

`StatelessSinkPartition()`
:   Output partition that is stateless.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * bytewax.connectors.kafka._KafkaSinkPartition
    * bytewax.connectors.stdio._PrintSinkPartition
    * bytewax.testing._ListSinkPartition

    ### Methods

    `close(self) ‑> None`
    :   Cleanup this partition when the dataflow completes.

        This is not guaranteed to be called. It will only be called
        when the dataflow finishes on finite input. It will not be
        called during an abrupt or abort shutdown.

    `write_batch(self, items: List[Any]) ‑> None`
    :   Write a batch of output items.

        Called multiple times whenever new items are seen at this
        point in the dataflow.

        Args:
            items:
                Items in the dataflow. Non-deterministically batched.
