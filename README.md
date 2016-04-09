# toxic
Small .dot file transformation utility

## Requirements
- Python 3.5+
- pydot-ng

## Usage

On Unix-like systems like GNU/Linux and OS X, `toxic.py` is directly executable
(provided that Python 3.5+ is installed):

<pre>
$ toxic.py <em>ARGUMENTS</em>
</pre>

On Windows, `toxic.py` should be invoked explicitly via the Python interpreter:

<pre>
C:\toxic> python toxic.py <em>ARGUMENTS</em>
</pre>

All examples below follow the Unix-style invocation, but deducing their Windows
counterpart is straightfoward.

### Command-line options

`toxic.py` requires two command-line options for the basic parameters of the
transformation.  Both short and long option forms are available:

- <code>-t *THRESHOLD*</code>, <code>--threshold=*THRESHOLD*</code> weight
  threshold value.  Edges with weight below the threshold are deleted from the
  graph.
- <code>-r *NODE*</code>, <code>--gc-root=*NODE*</code> the label of the node to
  be used as a root during the garbage collection (GC) phase.  This option may
  be used multiple times to specify multiple GC roots.

### Pipe mode

When invoked without filename arguments, `toxic.py` reads .dot data from
standard input and writes transformed .dot data to the standard output:

```
$ cat input.dot | toxic.py -t 0.09 -r C6H6 -r C7H8 > output.dot
```

Transforming standard input to standard output allows `toxic.py` to participate
as an element of a longer pipe chain.  For example:

```
$ cat input.dot | toxic.py -t 0.09 -r C6H6 -r C7H8 | dot -Tpng | open -f -a /Applications/Preview.app
```

### File mode

When invoked with two filename arguments, `toxic.py` reads .dot data from the
first file and writes transformed .dot data to the second file:

```
$ toxic.py --threshold=0.09 --gc-root=C6H6 input.dot output.dot
```

WARNING: If the output file already exists, it will be *overwritten*.


### Directory mode

When both both arguments are directories, `toxic.py` reads all .dot files from
the first directory and writes transformed files to the second directory:

```
$ toxic.py --threshold=0.09 --gc-root=C6H6 input_dir/ output_dir/
```

WARNING: Exising files in the output directory will be *overwritten*.
