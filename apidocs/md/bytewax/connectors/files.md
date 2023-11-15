Module bytewax.connectors.files
===============================
Connectors for local text files.

Classes
-------

`CSVSource(path: pathlib.Path, batch_size: int = 1000, get_fs_id: Callable[[pathlib.Path], str] = <function _get_path_dev>, **fmtparams)`
:   Read a path as a CSV file row-by-row as keyed-by-column dicts.

    The path must exist on at least one worker. Each worker can have a
    unique file at the path if each worker mounts a distinct
    filesystem. Tries to read only one instance of each unique file in
    the whole cluster by deduplicating paths by filesystem ID. See
    `get_fs_id` to adjust this.

    Unique files are the unit of parallelism; only one worker will
    read each unique file. Thus, lines from different files are
    interleaved.

    Sample input:

    ```
    index,timestamp,value,instance
    0,2022-02-24 11:42:08,0.132,24ae8d
    0,2022-02-24 11:42:08,0.066,c6585a
    0,2022-02-24 11:42:08,42.652,ac20cd
    ```

    Sample output:

    ```
    {
      'index': '0',
      'timestamp': '2022-02-24 11:42:08',
      'value': '0.132',
      'instance': '24ae8d'
    }
    {
      'index': '0',
      'timestamp': '2022-02-24 11:42:08',
      'value': '0.066',
      'instance': 'c6585a'
    }
    {
      'index': '0',
      'timestamp': '2022-02-24 11:42:08',
      'value': '42.652',
      'instance': 'ac20cd'
    }
    ```

    Init.

    Args:
        path: Path to file.

        batch_size: Number of lines to read per batch. Defaults to
            1000.

        get_fs_id: Called with the parent directory and must
            return a consistent (across workers and restarts)
            unique ID for the filesystem of that directory.
            Defaults to using `os.stat_result.st_dev`.

            If you know all workers have access to identical
            files, you can have this return a constant: `lambda
            _dir: "SHARED"`.

        **fmtparams: Any custom formatting arguments you can pass
            to
            [`csv.reader`](https://docs.python.org/3/library/csv.html?highlight=csv#csv.reader).

    ### Ancestors (in MRO)

    * bytewax.connectors.files.FileSource
    * bytewax.inputs.FixedPartitionedSource
    * bytewax.inputs.Source
    * abc.ABC

`DirSink(dir_path: pathlib.Path, file_count: int, file_namer: Callable[[int, int], str] = <function DirSink.<lambda>>, assign_file: Callable[[str], int] = <function DirSink.<lambda>>, end: str = '\n')`
:   Write to a set of files in a filesystem directory line-by-line.

    Items consumed from the dataflow must look like two-tuples of
    `(key, value)`, where the value must look like a string. Use a
    proceeding map step to do custom formatting.

    The directory must exist and contain identical data on all
    workers, so either run on a single machine or use a shared mount.

    Individual files are the unit of parallelism.

    Can support exactly-once processing in a batch context. Each file
    will be truncated during resume so duplicates are
    prevented. Tailing the output files will result in undefined
    behavior.

    Init.

    Args:
        dir_path:
            Path to directory.
        file_count:
            Number of separate partition files to create.
        file_namer:
            Will be called with two arguments, the file index and
            total file count, and must return the file name to use
            for that file partition. Defaults to naming files like
            `"part_{i}"`, where `i` is the file index.
        assign_file:
            Will be called with the key of each consumed item and
            must return the file index the value will be written
            to. Will wrap to the file count if you return a larger
            value. Defaults to calling `zlib.adler32` as a simple
            globally-consistent hash.
        end:
            String to write after each item. Defaults to newline.

    ### Ancestors (in MRO)

    * bytewax.outputs.FixedPartitionedSink
    * bytewax.outputs.Sink
    * abc.ABC

    ### Methods

    `build_part(self, for_part, resume_state)`
    :   See ABC docstring.

    `list_parts(self)`
    :   Each file is a partition.

    `part_fn(self, item_key)`
    :   Use the specified file assigner.

`DirSource(dir_path: pathlib.Path, glob_pat: str = '*', batch_size: int = 1000, get_fs_id: Callable[[pathlib.Path], str] = <function _get_path_dev>)`
:   Read all files in a filesystem directory line-by-line.

    The directory must exist on at least one worker. Each worker can
    have unique files at overlapping paths if each worker mounts a
    distinct filesystem. Tries to read only one instance of each
    unique file in the whole cluster by deduplicating paths by
    filesystem ID. See `get_fs_id` to adjust this.

    Unique files are the unit of parallelism; only one worker will
    read each unique file. Thus, lines from different files are
    interleaved.

    Can support exactly-once processing.

    Init.

    Args:
        dir_path: Path to directory.

        glob_pat: Pattern of files to read from the directory.
            Defaults to `"*"` or all files.

        batch_size: Number of lines to read per batch. Defaults to
            1000.

        get_fs_id: Called with the directory and must return a
            consistent (across workers and restarts) unique ID for
            the filesystem of that directory. Defaults to using
            `os.stat_result.st_dev`.

            If you know all workers have access to identical
            files, you can have this return a constant: `lambda
            _dir: "SHARED"`.

    ### Ancestors (in MRO)

    * bytewax.inputs.FixedPartitionedSource
    * bytewax.inputs.Source
    * abc.ABC

    ### Methods

    `build_part(self, _now: datetime.datetime, part_key: str, resume_state: Optional[Any])`
    :   See ABC docstring.

    `list_parts(self)`
    :   Each file is a separate partition.

`FileSink(path: pathlib.Path, end: str = '\n')`
:   Write to a single file line-by-line on the filesystem.

    Items consumed from the dataflow must look like a string. Use a
    proceeding map step to do custom formatting.

    The file must exist and be identical on all workers.

    There is no parallelism; only one worker will actually write to
    the file.

    Can support exactly-once processing in a batch context. The file
    will be truncated during resume so duplicates are
    prevented. Tailing the output file will result in undefined
    behavior.

    Init.

    Args:
        path:
            Path to file.
        end:
            String to write after each item. Defaults to newline.

    ### Ancestors (in MRO)

    * bytewax.outputs.FixedPartitionedSink
    * bytewax.outputs.Sink
    * abc.ABC

    ### Methods

    `build_part(self, for_part, resume_state)`
    :   See ABC docstring.

    `list_parts(self)`
    :   The file is a single partition.

    `part_fn(self, item_key)`
    :   Only one partition.

`FileSource(path: Union[pathlib.Path, str], batch_size: int = 1000, get_fs_id: Callable[[pathlib.Path], str] = <function _get_path_dev>)`
:   Read a path line-by-line from the filesystem.

    The path must exist on at least one worker. Each worker can have a
    unique file at the path if each worker mounts a distinct
    filesystem. Tries to read only one instance of each unique file in
    the whole cluster by deduplicating paths by filesystem ID. See
    `get_fs_id` to adjust this.

    Unique files are the unit of parallelism; only one worker will
    read each unique file. Thus, lines from different files are
    interleaved.

    Init.

    Args:
        path: Path to file.

        batch_size: Number of lines to read per batch. Defaults to
            1000.

        get_fs_id: Called with the parent directory and must
            return a consistent (across workers and restarts)
            unique ID for the filesystem of that directory.
            Defaults to using `os.stat_result.st_dev`.

            If you know all workers have access to identical
            files, you can have this return a constant: `lambda
            _dir: "SHARED"`.

    ### Ancestors (in MRO)

    * bytewax.inputs.FixedPartitionedSource
    * bytewax.inputs.Source
    * abc.ABC

    ### Descendants

    * bytewax.connectors.files.CSVSource

    ### Methods

    `build_part(self, _now: datetime.datetime, part_key: str, resume_state: Optional[Any])`
    :   See ABC docstring.

    `list_parts(self)`
    :   The file is a single partition.
