Module bytewax.serde
====================
Serialization for recovery and transport.

Classes
-------

`JsonPickleSerde()`
:   Serialize objects using `jsonpickle`.

    See [`jsonpickle`](https://github.com/jsonpickle/jsonpickle) for
    more info.

    ### Ancestors (in MRO)

    * bytewax.serde.Serde
    * abc.ABC

    ### Static methods

    `de(s)`
    :   See ABC docstring.

    `ser(obj)`
    :   See ABC docstring.

`Serde()`
:   A serialization format.

    This must support serializing arbitray Python objects and
    reconstituting them exactly. This means using things like
    `json.dumps` and `json.loads` directly will not work, as they do
    not support things like datetimes, integer keys, etc.

    Even if all of your dataflow's state is serializeable by a format,
    Bytewax generates Python objects to store internal data, and they
    must round-trip correctly or there will be errors.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * bytewax.serde.JsonPickleSerde

    ### Static methods

    `de(s: str) ‑> Any`
    :   Deserialize the given object.

    `ser(obj: Any) ‑> str`
    :   Serialize the given object.
