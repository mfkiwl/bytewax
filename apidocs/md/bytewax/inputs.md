Module bytewax.inputs
=====================
Low-level input interfaces and input helpers.

If you want pre-built connectors for various external systems, see
`bytewax.connectors`. That is also a rich source of examples.

Subclass the types here to implement input for your own custom source.

Functions
---------


`batch(ib: Iterable[Any], batch_size: int) ‑> Iterator[List[Any]]`
:   Batch an iterable.

    Use this to easily generate batches of items for a source's
    `next_batch` method.

    Args:
        ib:
            The underlying source iterable of items.
        batch_size:
            Maximum number of items to yield in a batch.

    Yields:
        The next gathered batch of items.


`batch_async(aib: collections.abc.AsyncIterable, timeout: datetime.timedelta, batch_size: int, loop=None) ‑> Iterator[List[Any]]`
:   Batch an async iterable synchronously up to a timeout.

    This allows using an async iterator as an input source. The
    `next_batch` method on an input source must never block, this
    allows running an async iterator up to a timeout so that you
    correctly cooperatively multitask with the rest of the dataflow.

    Args:
        aib:
            The underlying source async iterable of items.
        timeout:
            Duration of time to repeatedly poll the source
            async iterator for items.
        batch_size:
            Maximum number of items to yield in a batch, even if
            the timeout has not been hit.
        loop:
            Custom `asyncio` run loop to use, if any.

    Yields:
        The next gathered batch of items.

        This function will take up to `timeout` time to yield, or
        will return a list with length up to `max_len`.


`batch_getter(getter: Callable[[], Any], batch_size: int, yield_on: Any = None) ‑> Iterator[List[Any]]`
:   Batch from a getter function that might not return an item.

     Use this to easily generate batches of items for a source's
    `next_batch` method.

    Args:
        getter:
            Function to call to get the next item. Should raise
            `StopIteration` on EOF.

        batch_size:
            Maximum number of items to yield in a batch.

        yield_on:
            Sentinel value that indicates that there are no more items
            yet, and to return the current batch. Defaults to `None`.

    Yields:
        The next gathered batch of items.


`batch_getter_ex(getter: Callable[[], Any], batch_size: int, yield_ex: Type[Exception] = _queue.Empty) ‑> Iterator[List[Any]]`
:   Batch from a getter function that raises on no items yet.

     Use this to easily generate batches of items for a source's
    `next_batch` method.

    Args:
        getter:
            Function to call to get the next item. Should raise
            `StopIteration` on EOF.

        batch_size:
            Maximum number of items to return in a batch.

        yield_ex:
            Exception raised by `getter` that indicates that there are
            no more items yet, and to return the current
            batch. Defaults to `queue.Empty`.

    Yields:
        The next gathered batch of items.

Classes
-------

`AbortExecution(*args, **kwargs)`
:   Raise this from `next_batch` to abort for testing purposes.

    ### Ancestors (in MRO)

    * builtins.RuntimeError
    * builtins.Exception
    * builtins.BaseException

`DynamicSource()`
:   An input source where all workers can read distinct items.

    Does not support storing any resume state. Thus these kind of
    sources only naively can support at-most-once processing.

    The source must somehow support supplying disjoint data for each
    worker. If you re-read the same items on multiple workers, the
    dataflow will process these as duplicate items.

    ### Ancestors (in MRO)

    * bytewax.inputs.Source
    * abc.ABC

    ### Methods

    `build(self, now: datetime.datetime, worker_index: int, worker_count: int) ‑> bytewax.inputs.StatelessSourcePartition`
    :   Build an input source for a worker.

        Will be called once on each worker.

        Args:
            now: The current time.

            worker_index: Index of this worker.

            worker_count: Total number of workers.

        Returns:
            The built partition.

`FixedPartitionedSource()`
:   An input source with a fixed number of independent partitions.

    Will maintain the state of each source and re-build using it
    during resume. If the source supports seeking, this input can
    support exactly-once processing.

    Each partition must contain unique data. If you re-read the same data
    in multiple partitions, the dataflow will process these duplicate
    items.

    ### Ancestors (in MRO)

    * bytewax.inputs.Source
    * abc.ABC

    ### Descendants

    * bytewax.connectors.files.DirSource
    * bytewax.connectors.files.FileSource
    * bytewax.connectors.kafka.KafkaSource
    * bytewax.inputs.SimplePollingSource
    * bytewax.testing.TestingSource

    ### Methods

    `build_part(self, now: datetime.datetime, for_part: str, resume_state: Optional[Any]) ‑> bytewax.inputs.StatefulSourcePartition`
    :   Build anew or resume an input partition.

        Will be called once per execution for each partition key on a
        worker that reported that partition was local in `list_parts`.

        Do not pre-build state about a partition in the
        constructor. All state must be derived from `resume_state` for
        recovery to work properly.

        Args:
            now: The current time.

            for_part: Which partition to build. Will always be one of
                the keys returned by `list_parts` on this worker.

            resume_state: State data containing where in the input
                stream this partition should be begin reading during
                this execution.

        Returns:
            The built partition.

    `list_parts(self) ‑> List[str]`
    :   List all local partitions this worker has access to.

        You do not need to list all partitions globally.

        Returns:
            Local partition keys.

`SimplePollingSource(interval: datetime.timedelta, align_to: Optional[datetime.datetime] = None)`
:   Calls a user defined function at a regular interval.

    >>> class URLSource(SimplePollingSource):
    ...     def __init__(self):
    ...         super(interval=timedelta(seconds=10))
    ...
    ...     def next_item(self):
    ...         res = requests.get("https://example.com")
    ...         if not res.ok:
    ...             raise SimplePollingSource.Retry(timedelta(seconds=1))
    ...         return res.text

    There is no parallelism; only one worker will poll this source.

    Does not support storing any resume state. Thus these kind of
    sources only naively can support at-most-once processing.

    This is best for low-throughput polling on the order of seconds to
    hours.

    If you need a high-throughput source, or custom retry or timing,
    avoid this. Instead create a source using one of the other
    `Source` subclasses where you can have increased paralellism,
    batching, and finer control over timing.

    Init.

    Args:
        interval:
            The interval between calling `next_item`.
        align_to:
            Align awake times to the given datetime. Defaults to
            now.

    ### Ancestors (in MRO)

    * bytewax.inputs.FixedPartitionedSource
    * bytewax.inputs.Source
    * abc.ABC

    ### Class variables

    `Retry`
    :   Raise this to try to get items before the usual interval.

        Args:
            timeout: How long to wait before calling
                `SimplePollingSource.next_item` again.

    ### Methods

    `build_part(self, now: datetime.datetime, _for_part: str, _resume_state: Optional[Any])`
    :   See ABC docstring.

    `list_parts(self)`
    :   Assumes the source has a single partition.

    `next_item(self) ‑> Any`
    :   Override with custom logic to poll your source.

        Raises:
            Retry: Raise if you can't fetch items and would like to
                call this function sooner than the usual interval.

        Returns:
            Next item to emit into the dataflow. If `None`, no item is
            emitted.

`Source()`
:   A location to read input items from.

    Base class for all input sources. Do not subclass this.

    If you want to implement a custom connector, instead subclass one
    of the specific source sub-types below in this module.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * bytewax.inputs.DynamicSource
    * bytewax.inputs.FixedPartitionedSource

`StatefulSourcePartition()`
:   Input partition that maintains state of its position.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * bytewax.connectors.files._CSVPartition
    * bytewax.connectors.files._FileSourcePartition
    * bytewax.connectors.kafka._KafkaSourcePartition
    * bytewax.inputs._SimplePollingPartition
    * bytewax.testing._IterSourcePartition

    ### Methods

    `close(self) ‑> None`
    :   Cleanup this partition when the dataflow completes.

        This is not guaranteed to be called. It will only be called
        when the dataflow finishes on finite input. It will not be
        called during an abrupt or abort shutdown.

    `next_awake(self) ‑> Optional[datetime.datetime]`
    :   When to next attempt to get input items.

        `next_batch()` will not be called until the most recently returned
        time has past.

        This will be called upon initialization of the source and
        after `next_batch()`, but also possibly at other times. Multiple
        times are not stored; you must return the next awake time on
        every call, if any.

        If this returns `None`, `next_batch()` will be called
        immediately unless the previous batch had no items, in which
        case there is a 1 millisecond delay.

        Use this instead of `time.sleep` in `next_batch()`.

        Returns:
            Next awake time or `None` to indicate automatic behavior.

    `next_batch(self, sched: datetime.datetime) ‑> List[Any]`
    :   Attempt to get the next batch of input items.

        This must participate in a kind of cooperative multi-tasking,
        never blocking but returning an empty list if there are no
        items to emit yet.

        Args:
            sched: The scheduled awake time.

        Returns:
            An list of items immediately ready. May be empty if no new
            items.

        Raises:
            StopIteration: When the source is complete.

    `snapshot(self) ‑> Any`
    :   Snapshot the position of the next read of this partition.

        This will be returned to you via the `resume_state` parameter
        of your input builder.

        Be careful of "off by one" errors in resume state. This should
        return a state that, when built into a partition, resumes reading
        _after the last read item item_, not the same item that
        `next()` last returned.

        This is guaranteed to never be called after `close()`.

        Returns:
            Resume state.

`StatelessSourcePartition()`
:   Input partition that is stateless.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Methods

    `close(self) ‑> None`
    :   Cleanup this partition when the dataflow completes.

        This is not guaranteed to be called. It will only be called
        when the dataflow finishes on finite input. It will not be
        called during an abrupt or abort shutdown.

    `next_awake(self) ‑> Optional[datetime.datetime]`
    :   When to next attempt to get input items.

        `next_batch()` will not be called until the most recently returned
        time has past.

        This will be called upon initialization of the source and
        after `next_batch()`, but also possibly at other times. Multiple
        times are not stored; you must return the next awake time on
        every call, if any.

        If this returns `None`, `next_batch()` will be called
        immediately unless the previous batch had no items, in which
        case there is a 1 millisecond delay.

        Use this instead of `time.sleep` in `next_batch()`.

        Returns:
            Next awake time or `None` to indicate automatic behavior.

    `next_batch(self, sched: datetime.datetime) ‑> List[Any]`
    :   Attempt to get the next batch of input items.

        This must participate in a kind of cooperative multi-tasking,
        never blocking but yielding an empty list if there are no new
        items yet.

        Args:
            sched: The scheduled awake time.

        Returns:
            An list of items immediately ready. May be empty if no new
            items.

        Raises:
            StopIteration: When the source is complete.
