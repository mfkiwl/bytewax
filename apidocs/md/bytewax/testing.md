Module bytewax.testing
======================
Helper tools for testing dataflows.

Functions
---------


`cluster_main(flow, addresses, proc_id, *, epoch_interval=None, recovery_config=None, worker_count_per_proc=1)`
:   Execute a dataflow in the current process as part of a cluster.

    This is only used for unit testing. See `bytewax.run`.

    Blocks until execution is complete.

    >>> from bytewax.dataflow import Dataflow
    >>> from bytewax.testing import TestingInput
    >>> from bytewax.connectors.stdio import StdOutput
    >>> flow = Dataflow()
    >>> flow.input("inp", TestingInput(range(3)))
    >>> flow.capture(StdOutput())
    >>> addresses = []  # In a real example, you'd find the "host:port" of all other Bytewax workers.
    >>> proc_id = 0  # In a real example, you'd assign each worker a distinct ID from 0..proc_count.
    >>> cluster_main(flow, addresses, proc_id)
    0
    1
    2

    Args:

      flow: Dataflow to run.

      addresses: List of host/port addresses for all processes in
          this cluster (including this one).

      proc_id: Index of this process in cluster; starts from 0.

      epoch_interval (datetime.timedelta): System time length of each
          epoch. Defaults to 10 seconds.

      recovery_config (bytewax.recovery.RecoveryConfig): State
          recovery config. If `None`, state will not be persisted.

      worker_count_per_proc: Number of worker threads to start on
          each process.


`ffwd_iter(it: Iterator[Any], n: int) ‑> None`
:   Skip an iterator forward some number of items.

    Args:
        it:
            A stateful iterator to advance.
        n:
            Number of items to skip from the current position.


`poll_next_batch(part, timeout=datetime.timedelta(seconds=5))`
:   Repeatedly poll an input source until it returns a batch.

    You'll want to use this in unit tests of sources when there's some
    non-determinism in how items are read.

    This is a busy-loop.

    Args:
        part: To call `next` on.

        timeout: How long to continuously poll for.

    Returns:
        The next batch found.

    Raises:
        TimeoutError: If no batch was returned within the timeout.


`run_main(flow, *, epoch_interval=None, recovery_config=None)`
:   Execute a dataflow in the current thread.

    Blocks until execution is complete.

    This is only used for unit testing. See `bytewax.run`.

    >>> from bytewax.dataflow import Dataflow
    >>> from bytewax.testing import TestingInput, run_main
    >>> from bytewax.connectors.stdio import StdOutput
    >>> flow = Dataflow()
    >>> flow.input("inp", TestingInput(range(3)))
    >>> flow.capture(StdOutput())
    >>> run_main(flow)
    0
    1
    2

    Args:

      flow: Dataflow to run.

      epoch_interval (datetime.timedelta): System time length of each
          epoch. Defaults to 10 seconds.

      recovery_config (bytewax.recovery.RecoveryConfig): State
          recovery config. If `None`, state will not be persisted.

Classes
-------

`TestingSink(ls)`
:   Append each output item to a list.

    You only want to use this for unit testing.

    Can support at-least-once processing. The list is not cleared
    between executions.

    Init.

    Args:
        ls: List to append to.

    ### Ancestors (in MRO)

    * bytewax.outputs.DynamicSink
    * bytewax.outputs.Sink
    * abc.ABC

    ### Methods

    `build(self, worker_index, worker_count)`
    :   See ABC docstring.

`TestingSource(ib: Iterable[Any], batch_size: int = 1)`
:   Produce input from a Python iterable.

    You only want to use this for unit testing.

    The iterable must be identical on all workers.

    There is no parallelism; only one worker will actually consume the
    iterable.

    Be careful using a generator as the iterable; if you fail and
    attempt to resume the dataflow without rebuilding it, the
    half-consumed generator will be re-used on recovery and early
    input will be lost so resume will see the correct data.

    Init.

    Args:
        ib: Iterable for input.

        batch_size: Number of items from the iterable to emit in
            each batch. Defaults to 1.

    ### Ancestors (in MRO)

    * bytewax.inputs.FixedPartitionedSource
    * bytewax.inputs.Source
    * abc.ABC

    ### Class variables

    `ABORT`
    :   Abort the execution when the input processes this item.

        The next execution will resume from some item befor this one.

        Each abort will only trigger once. They'll be skipped on
        resume executions.

    `EOF`
    :   Signal the input to EOF.

        The next execution will continue from the item after this.

    ### Methods

    `build_part(self, now: datetime.datetime, for_key: str, resume_state: Optional[Any])`
    :   See ABC docstring.

    `list_parts(self)`
    :   The iterable is read on a single worker.
