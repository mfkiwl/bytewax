from bytewax.connectors.stdio import StdOutSink
from bytewax.dataflow import Dataflow
from bytewax.testing import TestingSource, run_main


def test_std_output(capfd):
    flow = Dataflow()

    inp = ["a", "b"]
    flow.input("inp", TestingSource(inp))

    flow.output("out", StdOutSink())

    run_main(flow)

    captured = capfd.readouterr()
    assert captured.out == "a\nb\n"
