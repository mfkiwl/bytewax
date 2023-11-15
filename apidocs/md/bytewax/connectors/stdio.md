Module bytewax.connectors.stdio
===============================
Connectors to console IO.

Classes
-------

`StdOutSink()`
:   Write each output item to stdout on that worker.

    Items consumed from the dataflow must look like a string. Use a
    proceeding map step to do custom formatting.

    Workers are the unit of parallelism.

    Can support at-least-once processing. Messages from the resume
    epoch will be duplicated right after resume.

    ### Ancestors (in MRO)

    * bytewax.outputs.DynamicSink
    * bytewax.outputs.Sink
    * abc.ABC

    ### Methods

    `build(self, worker_index, worker_count)`
    :   See ABC docstring.
