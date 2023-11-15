Module bytewax.window
=====================
Time-based windows.

Bytewax provides some operators and pre-built configurations for
easily grouping data into buckets called **windows** and running code
on just the values in those windows.

See the operator methods on `bytewax.dataflow.Dataflow` with `_window`
in the name for simple example use cases of each.

Use
---

1. Pick a clock and create a config for it. A **clock** determines the
time of each element and the current time used for closing each
window. E.g. use the current system time. See the docs for each
subclass of `ClockConfig` for options.

2. Pick a windower and create a config for it. A **windower** defines
how to take the values and their times and bucket them into
windows. E.g. have tumbling windows every 30 seconds. See the docs for
each subclass of `WindowConfig` for options.

3. Pick a **key** to route the values for the window and make sure the
input to the windowing operator you choose is a 2-tuple of `(key: str,
value)`. Windows are managed independently for each key. If you need
all data to be processed into the same window state, you can use a
constant key like `("ALL", value)` but this will reduce the
parallelism possible in the dataflow. This is similar to all the other
stateful operators, so you can read more on their methods on
`bytewax.dataflow.Dataflow`.

4. Pass both these configs to the windowing operator of your
choice. The **windowing operators** decide what kind of logic you
should apply to values within a window and what should be the output
of the window. E.g. `bytewax.dataflow.Dataflow.reduce_window` combines
all values in a window into a single output and sends that downstream.

You are allowed and encouraged to have as many different clocks and
windowers as you need in a single dataflow. Just instantiate more of
them and pass the ones you need for each situation to each windowing
operator.

Order
-----

Because Bytewax can be run as a distributed system with multiple
worker processes and threads all reading relevant data simultaneously,
you have to specifically collect and manually sort data that you need
to process in strict time order.

Output
------

Output from windowing operators is in the form of
`(key, (metadata, values))` where metadata is an instance of
`bytewax.window.WindowMetadata`.

Recovery
--------

Bytewax's windowing system is built on top of its recovery system (see
`bytewax.run` for more info), so failure in the middle of a window
will be handled as gracefully as possible.

Some clocks don't have a single correct answer on what to do during
recovery. E.g. if you use `SystemClockConfig` with 10 minute windows,
but then recover on a 15 minute mark, the system will immediately
close out the half-completed window stored during recovery. See the
docs for each `ClockConfig` subclass for specific notes on recovery.

Recovery happens on the granularity of the _epochs_ of the dataflow,
not the windows. Epoch interval has no affect on windowing operator
behavior when there are no failures; it is solely an implementation
detail of the recovery system. See `bytewax.run` for more information
on epochs.

Classes
-------

`ClockConfig()`
:   Base class for a clock config.

    This describes how a windowing operator should determine the
    current time and the time for each element.

    Use a specific subclass of this that matches the time definition
    you'd like to use.

    ### Descendants

    * bytewax.window.EventClockConfig
    * bytewax.window.SystemClockConfig

`EventClockConfig(dt_getter, wait_for_system_duration)`
:   Use a getter function to lookup the timestamp for each item.

    The watermark is the largest item timestamp seen thus far, minus
    the waiting duration, plus the system time duration that has
    elapsed since that item was seen. This effectively means items
    will be correctly processed as long as they are not out of order
    more than the waiting duration in system time.

    If the dataflow has no more input, all windows are closed.

    Args:
      dt_getter:
        Python function to get a datetime from an event. The datetime
        returned must have tzinfo set to
        `timezone.utc`. E.g. `datetime(1970, 1, 1,
        tzinfo=timezone.utc)`
      wait_for_system_duration:
        How much system time to wait before considering an event late.

    Returns:
      Config object. Pass this as the `clock_config` parameter to
      your windowing operator.

    ### Ancestors (in MRO)

    * bytewax.window.ClockConfig

    ### Instance variables

    `dt_getter`
    :   Return an attribute of instance, which is of type owner.

    `wait_for_system_duration`
    :   Return an attribute of instance, which is of type owner.

`SessionWindow(gap)`
:   Session windowing with a fixed inactivity gap.
    Each time a new item is received, it is added to the latest
    window if the time since the latest event is < gap.
    Otherwise a new window is created that starts at current clock's time.

     Args:
       gap (datetime.timedelta):
         Gap of inactivity before considering a session closed. The
         gap should not be negative.

    Returns:
      Config object. Pass this as the `window_config` parameter to
      your windowing operator.

    ### Ancestors (in MRO)

    * bytewax.window.WindowConfig

    ### Instance variables

    `gap`
    :   Return an attribute of instance, which is of type owner.

`SlidingWindow(length, offset, align_to)`
:   Sliding windows of fixed duration.

    If offset == length, windows cover all time but do not
    overlap. Each item will fall in exactly one window. The
    `TumblingWindow` config will do this for you.

    If offset < length, windows overlap. Each item will fall in
    multiple windows.

    If offset > length, there will be gaps between windows. Each item
    can fall in up to one window, but might fall into none.

    Window start times are inclusive, but end times are exclusive.

    Args:
      length (datetime.timedelta):
        Length of windows.
      offset (datetime.timedelta):
        Duration between start times of adjacent windows.
      align_to (datetime.datetime):
        Align windows so this instant starts a window. This must be a
        constant. You can use this to align all windows to hour
        boundaries, e.g.

    Returns:
      Config object. Pass this as the `window_config` parameter to
      your windowing operator.

    ### Ancestors (in MRO)

    * bytewax.window.WindowConfig

    ### Instance variables

    `align_to`
    :   Return an attribute of instance, which is of type owner.

    `length`
    :   Return an attribute of instance, which is of type owner.

    `offset`
    :   Return an attribute of instance, which is of type owner.

`SystemClockConfig()`
:   Use the current system time as the timestamp for each item.

    The watermark is also the current system time.

    If the dataflow has no more input, all windows are closed.

    Returns:
      Config object. Pass this as the `clock_config` parameter to
      your windowing operator.

    ### Ancestors (in MRO)

    * bytewax.window.ClockConfig

`TumblingWindow(length, align_to)`
:   Tumbling windows of fixed duration.

    Each item will fall in exactly one window.

    Window start times are inclusive, but end times are exclusive.

    Args:
      length (datetime.timedelta):
        Length of windows.
      align_to (datetime.datetime):
        Align windows so this instant starts a window. This must be a
        constant. You can use this to align all windows to hour
        boundaries, e.g.

    Returns:
      Config object. Pass this as the `window_config` parameter to
      your windowing operator.

    ### Ancestors (in MRO)

    * bytewax.window.WindowConfig

    ### Instance variables

    `align_to`
    :   Return an attribute of instance, which is of type owner.

    `length`
    :   Return an attribute of instance, which is of type owner.

`WindowConfig()`
:   Base class for a windower config.

    This describes the type of windows you would like.

    Use a specific subclass of this that matches the window definition
    you'd like to use.

    ### Descendants

    * bytewax.window.SessionWindow
    * bytewax.window.SlidingWindow
    * bytewax.window.TumblingWindow

`WindowMetadata(open_time, close_time)`
:   Metadata object for a window.

     Args:
       key (WindowKey):
         Internal window ID
       open_time (datetime.datetime)
         The time that the window starts.
       close_time (datetime.datetime)
         The time that the window closes. For some window
         types(SessionWindow), this value can change as new
         data is received.

    Returns:
      WindowMetadata object

    ### Instance variables

    `close_time`
    :   Return an attribute of instance, which is of type owner.

    `open_time`
    :   Return an attribute of instance, which is of type owner.
