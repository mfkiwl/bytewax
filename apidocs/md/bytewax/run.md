Module bytewax.run
==================
Executing dataflows.

Dataflows are run for local development or production by executing
this module as as script with `python -m bytewax.run`.

See `python -m bytewax.run --help` for more info.

If you need to execute a dataflow as part of running unit tests, see
`bytewax.testing`.

Execution
---------

You can run your Dataflow in 3 different ways
The first argument passed to this script is a dataflow getter string.
It should point to the python module containing the dataflow, and the
name of the variable holding the dataflow, or a function call that
returns a dataflow.

For example, if you are at the root of this repository, you can run the
"simple.py" example by calling the script with the following argument:

```
$ python -m bytewax.run examples.simple:flow
```

If instead of a variable, you have a function that returns a dataflow,
you can use a string after the `:` to call the function, possibly with args:

```
$ python -m bytewax.run "my_dataflow:get_flow('/tmp/file')"
```

By default this script will run a single worker on a single process.
You can modify this by using other parameters:

### Multiple workers

You can run a single processes with multiple workers, by
adding the `-w/--workers-per-process` parameter, without
changing anything in the code:

```
# Runs a process with 2 workers:
$ python -m bytewax.run my_dataflow -w2
```

### Multiple processes

You can also manually handle the multiple processes, and run them on different
machines, by using the `-a/--addresses` and `-i/--process-id` parameters.

Each process should receive a list of addresses of all the processes (the `-a`
parameter) and the id of the current process (a number starting from 0):

```
# First process
$ python -m bytewax.run my_dataflow     --addresses "localhost:2021;localhost:2022"     --process-id 0
```

```
# Second process
$ python -m bytewax.run my_dataflow     --addresses "localhost:2021;localhost:2022"     --process-id 1
```

Recovery
--------

See the `bytewax.recovery` module docstring for how to setup recovery.

Functions
---------


`cli_main(flow, *, workers_per_process=1, process_id=None, addresses=None, epoch_interval=None, recovery_config=None)`
:   This is only supposed to be used through `python -m
    bytewax.run`. See the module docstring for use.
