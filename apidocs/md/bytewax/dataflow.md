Module bytewax.dataflow
=======================
How to define dataflows.

Create a `Dataflow` instance, then use the methods on it to add
computational steps.

Classes
-------

`Dataflow()`
:   A definition of a Bytewax dataflow graph.

    Use the methods defined on this class to add steps with operators
    of the same name.

    ### Methods

    `batch(self, /, step_id, max_size, timeout)`
    :   Batch incoming items until either a batch size has been reached or a timeout has passed.
        This is a stateful operator.

        Args:
          step_id (str):
              Uniquely identifies this step for recovery.
          max_size (int):
              Maximum size of the batch.
          timeout (datetime.timedelta):
              Timeout before emitting the batch, even if max_size
              was not reached yet.

    `collect_window(self, /, step_id, clock_config, window_config)`
    :   Collect window lets emits all items for a key in a window
        downstream in sorted order.

        It is a stateful operator. It requires the upstream items are
        `(key: str, value)` tuples so we can ensure that all relevant
        values are routed to the relevant state. It also requires a
        step ID to recover the correct state.

        It emits `(key, list)` tuples downstream at the end of each
        window where `list` is sorted by the time assigned by the
        clock.

        Currently, data is permanently allocated per-key. If you have
        an ever-growing key space, note this.

        Args:
          step_id (str):
              Uniquely identifies this step.
          clock_config (bytewax.window.ClockConfig):
              Clock config to use. See `bytewax.window`.
          window_config (bytewax.window.WindowConfig):
              Windower config to use. See `bytewax.window`.

    `filter(self, /, step_id, predicate)`
    :   Filter selectively keeps only some items.

        It calls a **predicate** function on each item.

        It emits the item downstream unmodified if the predicate
        returns `True`.

        It is commonly used for:

        - Selecting relevant events
        - Removing empty events
        - Removing sentinels
        - Removing stop words

        >>> from bytewax.testing import TestingSource
        >>> from bytewax.connectors.stdio import StdOutSink
        >>> from bytewax.testing import run_main
        >>> from bytewax.dataflow import Dataflow
        >>>
        >>> flow = Dataflow()
        >>> flow.input("inp", TestingSource(range(4)))
        >>> def is_odd(item):
        ...     return item % 2 != 0
        >>> flow.filter("filter_odd", is_odd)
        >>> flow.output("out", StdOutSink())
        >>> run_main(flow)
        1
        3

        Args:
          step_id (str):
              Uniquely identifies this step.
          predicate:
              `predicate(item: Any) => should_emit: bool`

    `filter_map(self, /, step_id, mapper)`
    :   Filter map acts as a normal map function,
        but if the mapper returns None, the item
        is filtered out.

        >>> flow = Dataflow()
        >>> def validate(data):
        ...     if type(data) != dict or "key" not in data:
        ...         return None
        ...     else:
        ...         return data["key"], data
        ...
        >>> flow.filter_map("validate", validate)

        Args:
            step_id (str):
              Uniquely identifies this step.
            mapper:
                `mapper(item: Any) => modified_item: Optional[Any]`

    `flat_map(self, /, step_id, mapper)`
    :   Flat map is a one-to-many transformation of items.

        It calls a **mapper** function on each item.

        It emits each element in the returned iterator individually
        downstream in the epoch of the input item.

        It is commonly used for:

        - Tokenizing
        - Flattening hierarchical objects
        - Breaking up aggregations for further processing

        >>> from bytewax.testing import TestingSource
        >>> from bytewax.connectors.stdio import StdOutSink
        >>> from bytewax.testing import run_main
        >>> from bytewax.dataflow import Dataflow
        >>> flow = Dataflow()
        >>> inp = ["hello world"]
        >>> flow.input("inp", TestingSource(inp))
        >>> def split_into_words(sentence):
        ...     return sentence.split()
        >>> flow.flat_map("split_words", split_into_words)
        >>> flow.output("out", StdOutSink())
        >>> run_main(flow)
        hello
        world

        Args:
          step_id (str):
              Uniquely identifies this step.
          mapper:
              `mapper(item: Any) => emit: Iterable[Any]`

    `fold_window(self, /, step_id, clock_config, window_config, builder, folder)`
    :   Fold window lets you combine all items for a key within a
        window into an accumulator, using a function to build its initial value.

        It is like `Dataflow.reduce_window` but uses a function to
        build the initial value.

        It is a stateful operator. It requires the input stream
        has items that are `(key: str, value)` tuples so we can ensure
        that all relevant values are routed to the relevant state. It
        also requires a step ID to recover the correct state.

        It calls two functions:

        - A **builder** function which is called the first time a key appears
          and is expected to return the empty state for that key.

        - A **folder** which combines a new value with an accumulator.
          The accumulator is initially the output of the builder function.
          Values will be passed in window order, but no order
          is defined within a window.

        It emits `(key, (window_metadata, accumulator))` tuples downstream when the
        window closes.


        >>> from datetime import datetime, timedelta, timezone
        >>> from bytewax.dataflow import Dataflow
        >>> from bytewax.testing import run_main, TestingSource, TestingSink
        >>> from bytewax.window import TumblingWindow, EventClockConfig, WindowMetadata
        >>> align_to = datetime(2022, 1, 1, tzinfo=timezone.utc)
        >>>
        >>> flow = Dataflow()
        >>>
        >>> inp = [
        ...     ("ALL", {"time": align_to, "val": "a"}),
        ...     ("ALL", {"time": align_to + timedelta(seconds=4), "val": "b"}),
        ...     ("ALL", {"time": align_to + timedelta(seconds=8), "val": "c"}),
        ...     # The 10 second window should close just before processing this item.
        ...     ("ALL", {"time": align_to + timedelta(seconds=12), "val": "d"}),
        ...     ("ALL", {"time": align_to + timedelta(seconds=16), "val": "e"})
        ... ]
        >>>
        >>> flow.input("inp", TestingSource(inp))
        >>>
        >>> clock_config = EventClockConfig(
        ...     lambda e: e["time"], wait_for_system_duration=timedelta(seconds=0)
        ... )
        >>> window_config = TumblingWindow(length=timedelta(seconds=10), align_to=align_to)
        >>>
        >>> def add(acc, x):
        ...     acc.append(x["val"])
        ...     return acc
        >>>
        >>> flow.fold_window("sum", clock_config, window_config, list, add)
        >>>
        >>> out = []
        >>> flow.output("out", TestingSink(out))
        >>>
        >>> run_main(flow)
        >>> assert sorted(out) == sorted([
        ...     (
        ...         "ALL",
        ...         (
        ...             WindowMetadata(
        ...                 align_to, align_to + timedelta(seconds=10)
        ...             ),
        ...             ["a", "b", "c"]
        ...         ),
        ...     ),
        ...     (
        ...         "ALL",
        ...         (
        ...             WindowMetadata(
        ...                 align_to + timedelta(seconds=10), align_to + timedelta(seconds=20)
        ...             ),
        ...             ["d", "e"],
        ...         ),
        ...     ),
        ... ])

        Args:
          step_id (str):
              Uniquely identifies this step.
          clock_config (bytewax.window.ClockConfig):
              Clock config to use. See `bytewax.window`.
          window_config (bytewax.window.WindowConfig):
              Windower config to use. See `bytewax.window`.
          builder:
              `builder(key: Any) => initial_accumulator: Any`
          folder:
              `folder(accumulator: Any, value: Any) => updated_accumulator: Any`

    `input(self, /, step_id, source)`
    :   At least one input is required on every dataflow.

        Emits items downstream from the input source.

        See `bytewax.inputs` for more information on how input works.
        See `bytewax.connectors` for a buffet of our built-in
        connector types.

        Args:
          step_id (str):
              Uniquely identifies this step for recovery.
          source (bytewax.inputs.Source):
              Source to read items from.

    `inspect(self, /, inspector)`
    :   Inspect allows you to observe, but not modify, items.

        It calls an **inspector** callback on each item.

        It emits items downstream unmodified.

        It is commonly used for debugging.

        >>> from bytewax.testing import TestingSource, TestingSink
        >>> from bytewax.testing import run_main
        >>> from bytewax.dataflow import Dataflow
        >>> flow = Dataflow()
        >>> flow.input("inp", TestingSource(range(3)))
        >>> def log(item):
        ...     print("Saw", item)
        >>> flow.inspect(log)
        >>> out = []
        >>> flow.output("out", TestingSink(out))  # Notice we don't print out.
        >>> run_main(flow)
        Saw 0
        Saw 1
        Saw 2

        Args:
          inspector:
              `inspector(item: Any) => None`

    `inspect_epoch(self, /, inspector)`
    :   Inspect epoch allows you to observe, but not modify, items and
        their epochs.

        It calls an **inspector** function on each item with its
        epoch.

        It emits items downstream unmodified.

        It is commonly used for debugging.

        >>> from datetime import timedelta
        >>> from bytewax.testing import TestingSource, TestingSink, run_main
        >>> from bytewax.dataflow import Dataflow
        >>> flow = Dataflow()
        >>> flow.input("inp", TestingSource(range(3)))
        >>> def log(epoch, item):
        ...    print(f"Saw {item} @ {epoch}")
        >>> flow.inspect_epoch(log)
        >>> out = []
        >>> flow.output("out", TestingSink(out))  # Notice we don't print out.
        >>> run_main(flow, epoch_interval=timedelta(seconds=0))
        Saw 0 @ 1
        Saw 1 @ 2
        Saw 2 @ 3

        Args:
          inspector:
              `inspector(epoch: int, item: Any) => None`

    `inspect_worker(self, /, inspector)`
    :   Inspect worker allows you to observe, but not modify, items and
        their worker's index.

        It calls an **inspector** function on each item with its
        worker's index.

        It emits items downstream unmodified.

        It is commonly used for debugging.

        Args:
          inspector:
              `inspector(item: Any, worker: int) => None`

    `map(self, /, step_id, mapper)`
    :   Map is a one-to-one transformation of items.

        It calls a **mapper** function on each item.

        It emits each updated item downstream.

        It is commonly used for:

        - Extracting keys
        - Turning JSON into objects
        - So many things

        >>> from bytewax.connectors.stdio import StdOutSink
        >>> from bytewax.testing import run_main, TestingSource
        >>> from bytewax.dataflow import Dataflow
        >>> flow = Dataflow()
        >>> flow.input("inp", TestingSource(range(3)))
        >>> def add_one(item):
        ...     return item + 10
        >>> flow.map("add_one", add_one)
        >>> flow.output("out", StdOutSink())
        >>> run_main(flow)
        10
        11
        12

        Args:
          step_id (str):
              Uniquely identifies this step.
          mapper:
              `mapper(item: Any) => updated_item: Any`

    `output(self, /, step_id, sink)`
    :   Write data to an output.

        At least one output is required on every dataflow.

        Emits items downstream unmodified.

        See `bytewax.outputs` for more information on how output
        works. See `bytewax.connectors` for a buffet of our built-in
        connector types.

        Args:
          step_id (str):
              Uniquely identifies this step.
          sink (bytewax.outputs.Sink):
              Sink to write items to.

    `redistribute(self, /)`
    :   Redistribute items randomly across all workers for the next step.

        Bytewax's execution model has workers executing all steps, but
        the state in each step is partitioned across workers by some
        key. Bytewax will only exchange an item between workers before
        stateful steps in order to ensure correctness, that they
        interact with the correct state for that key. Stateless
        operators (like `filter`) are run on all workers and do not
        result in exchanging items before or after they are run.

        This can result in certain ordering of operators to result in
        poor parallelization across an entire execution cluster. If
        the previous step (like a `reduce_window` or `input` with a
        `PartitionedInput`) concentrated items on a subset of workers
        in the cluster, but the next step is a CPU-intensive stateless
        step (like a `map`), it's possible that not all workers will
        contribute to processing the CPU-intesive step.

        This operation has a overhead, since it will need
        to serialize, send, and deserialize the items,
        so while it can significantly speed up the
        execution in some cases, it can also make it slower.

        A good use of this operator is to parallelize an IO
        bound step, like a network request, or a heavy,
        single-cpu workload, on a machine with multiple
        workers and multiple cpu cores that would remain
        unused otherwise.

        A bad use of this operator is if the operation you want
        to parallelize is already really fast as it is, as the
        overhead can overshadow the advantages of distributing
        the work.
        Another case where you could see regressions in performance is
        if the heavy CPU workload already spawns enough threads
        to use all the available cores. In this case multiple
        processes trying to compete for the cpu can end up being
        slower than doing the work serially.
        If the workers run on different machines though, it might
        again be a valuable use of the operator.

        Use this operator with caution, and measure whether you
        get an improvement out of it.

        Once the work has been spread to another worker, it will
        stay on those workers unless other operators explicitely
        move the item again (usually on output).

    `reduce(self, /, step_id, reducer, is_complete)`
    :   Reduce lets you combine items for a key into an accumulator.

        It is a stateful operator. It requires the input stream
        has items that are `(key: str, value)` tuples so we can ensure
        that all relevant values are routed to the relevant state. It
        also requires a step ID to recover the correct state.

        It calls two functions:

        - A **reducer** which combines a new value with an
        accumulator. The accumulator is initially the first value seen
        for a key. Values will be passed in an arbitrary order. If
        there is only a single value for a key since the last
        completion, this function will not be called.

        - An **is complete** function which returns `True` if the most
        recent `(key, accumulator)` should be emitted downstream and
        the accumulator for that key forgotten. If there was only a
        single value for a key, it is passed in as the accumulator
        here.

        It emits `(key, accumulator)` tuples downstream when the is
        complete function returns `True` in the epoch of the most
        recent value for that key.

        If the ordering of values is crucial, group beforhand using a
        windowing operator with a timeout like `reduce_window`, then
        sort, then use this operator.

        It is commonly used for:

        - Collection into a list
        - Summarizing data

        >>> from bytewax.dataflow import Dataflow
        >>> from bytewax.testing import TestingSource, run_main
        >>> from bytewax.connectors.stdio import StdOutSink
        >>> flow = Dataflow()
        >>> inp = [
        ...     {"user": "a", "type": "login"},
        ...     {"user": "a", "type": "post"},
        ...     {"user": "b", "type": "login"},
        ...     {"user": "b", "type": "logout"},
        ...     {"user": "a", "type": "logout"},
        ... ]
        >>> flow.input("inp", TestingSource(inp))
        >>> def user_as_key(event):
        ...     return event["user"], [event]
        >>> flow.map("user_as_key", user_as_key)
        >>> def extend_session(session, events):
        ...     session.extend(events)
        ...     return session
        >>> def session_complete(session):
        ...     return any(event["type"] == "logout" for event in session)
        >>> flow.reduce("sessionizer", extend_session, session_complete)
        >>> flow.output("out", StdOutSink())
        >>> run_main(flow)
        ('b', [{'user': 'b', 'type': 'login'}, {'user': 'b', 'type': 'logout'}])
        ('a', [{'user': 'a', 'type': 'login'}, {'user': 'a', 'type': 'post'},
               {'user': 'a', 'type': 'logout'}])

        Args:
          step_id (str):
              Uniquely identifies this step.
          reducer:
              `reducer(accumulator: Any, value: Any) =>
              updated_accumulator: Any`
          is_complete:
              `is_complete(updated_accumulator: Any) =>
              should_emit: bool`

    `reduce_window(self, /, step_id, clock_config, window_config, reducer)`
    :   Reduce window lets you combine all items for a key within a
        window into an accumulator.

        It is like `Dataflow.reduce` but marks the
        accumulator as complete automatically at the end of each
        window.

        It is a stateful operator. It requires the input stream
        has items that are `(key: str, value)` tuples so we can ensure
        that all relevant values are routed to the relevant state. It
        also requires a step ID to recover the correct state.

        It calls a **reducer** function which combines two values. The
        accumulator is initially the first value seen for a key. Values
        will be passed in arbitrary order. If there is only a single
        value for a key in this window, this function will not be
        called.

        It emits `(key, (window_metadata, accumulator))` tuples downstream
        at the end of each window.

        If the ordering of values is crucial, group in this operator,
        then sort afterwards.

        Currently, data is permanently allocated per-key. If you have
        an ever-growing key space, note this.

        It is commonly used for:

        - Sessionization

        >>> from datetime import datetime, timedelta, timezone
        >>> from bytewax.testing import TestingSource, TestingSink, run_main
        >>> from bytewax.window import EventClockConfig, TumblingWindow
        >>> align_to = datetime(2022, 1, 1, tzinfo=timezone.utc)
        >>> flow = Dataflow()
        >>> inp = [
        ...     ("b", {"time": align_to, "val": 1}),
        ...     ("a", {"time": align_to + timedelta(seconds=4), "val": 1}),
        ...     ("a", {"time": align_to + timedelta(seconds=8), "val": 1}),
        ...     ("b", {"time": align_to + timedelta(seconds=12), "val": 1}),
        ... ]
        >>> flow.input("inp", TestingSource(inp))
        >>> def add(acc, x):
        ...     acc["val"] += x["val"]
        ...     return acc
        >>> clock_config = EventClockConfig(
        ...     lambda e: e["time"], wait_for_system_duration=timedelta(0)
        ... )
        >>> window_config = TumblingWindow(
        ...     length=timedelta(seconds=10), align_to=align_to
        ... )
        >>> flow.reduce_window("count", clock_config, window_config, add)
        >>> def extract_val(key__metadata_event):
        ...    key, (metadata, event) = key__metadata_event
        ...    return (key, event["val"])
        >>> flow.map("extract_val", extract_val)
        >>> out = []
        >>> flow.output("out", TestingSink(out))
        >>> run_main(flow)
        >>> assert sorted(out) == sorted([('b', 1), ('a', 2), ('b', 1)])

        Args:
          step_id (str):
              Uniquely identifies this step.
          clock_config (bytewax.window.ClockConfig):
              Clock config to use. See `bytewax.window`.
          window_config (bytewax.window.WindowConfig):
              Windower config to use. See `bytewax.window`.
          reducer: `reducer(accumulator: Any, value: Any) =>
              updated_accumulator: Any`

    `stateful_map(self, /, step_id, builder, mapper)`
    :   Stateful map is a one-to-one transformation of values, but
        allows you to reference a persistent state for each key when
        doing the transformation.

        It is a stateful operator. It requires the input stream
        has items that are `(key: str, value)` tuples so we can ensure
        that all relevant values are routed to the relevant state. It
        also requires a step ID to recover the correct state.

        It calls two functions:

        - A **builder** which returns a new state and will be called
        whenever a new key is encountered with the key as a parameter.

        - A **mapper** which transforms values. Values will be passed
        in an arbitrary order. If the updated state is `None`, the
        state will be forgotten.

        It emits a `(key, updated_value)` tuple downstream for each
        input item.

        If the ordering of values is crucial, group beforhand using a
        windowing operator with a timeout like `reduce_window`, then
        sort, then use this operator.

        It is commonly used for:

        - Anomaly detection
        - State machines

        >>> from bytewax.testing import TestingSource, run_main
        >>> from bytewax.connectors.stdio import StdOutSink
        >>> flow = Dataflow()
        >>> inp = [
        ...     "a",
        ...     "a",
        ...     "a",
        ...     "a",
        ...     "b",
        ... ]
        >>> flow.input("inp", TestingSource(inp))
        >>> def self_as_key(item):
        ...     return item, item
        >>> flow.map("self_as_key", self_as_key)
        >>> def build_count():
        ...     return 0
        >>> def check(running_count, item):
        ...     running_count += 1
        ...     if running_count == 1:
        ...         return running_count, item
        ...     else:
        ...         return running_count, None
        >>> flow.stateful_map("remove_duplicates", build_count, check)
        >>> def remove_none_and_key(key_item):
        ...     key, item = key_item
        ...     if item is None:
        ...         return []
        ...     else:
        ...         return [item]
        >>> flow.flat_map("remove_none_and_key", remove_none_and_key)
        >>> flow.output("out", StdOutSink())
        >>> run_main(flow)
        a
        b

        Args:
          step_id (str):
              Uniquely identifies this step.
          builder:
              `builder(key: Any) => new_state: Any`
          mapper:
              `mapper(state: Any, value: Any) => (updated_state:
              Any, updated_value: Any)`
