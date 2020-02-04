# MatchCopy

Python script for copying/moving pattern-matched files in source directory to some destination directory while maintaining the source directory's original tree structure. Can take in individual patterns at command line or via a .csv file. Additionally, will provide a receipt of "old" and "new" destinations for files as a .txt in same directory as script.

## Arguments

positional arguments

- `src`: path to source directory to match/copy/move from
- `dst`: path to destination directory to send matched files

optional arguments

- `-p, --patterns`: unix-style filename match patterns; supports '\*' and mutliple values separated by spaces

  - **ex.:** `-p testfile-01*`
  - **ex. (multi):** `-p testfile-01* some-other*pattern third-p*tt*rn`
  - **ex.:** `--patterns=testfile-01*`
  - **default:** `None`
  - **multi:** `True`

- `-i, --inputFile`: path to .csv file containing two columns ('pattern', 'extensions'), with each row as an individual pattern to match on. 'extensions' column allows for matching only certain file types.

  - **ex.:** `-i inputFile.csv`
  - **ex.:** `--inputFile=inputFile.csv`
  - **default:** `None`
  - **multi:** `False`

- `-e, --exts`: list of file extensions to filter matched files by

  - **note:** any 'extensions' column in passed inputFile overrides exts passed at command line as arguments
  - **ex.:** `-e .png`
  - **ex. (multi):** `-e .png .exr .ProRes`
  - **default:** `None`
  - **multi:** `True`
  - **note:** must include 'dot' ('.'), i.e. '.xlsx', '.png', etc.
  - **note:** if no file extensions passed in either .csv or at command line, then script will copy/move all files that matched a pattern, regardless of file type.

- `-m, --mode`: mode of copy when match found, i.e. copy (does not alter original file) vs 'move' (moves original file to dst directory)
  - **WARNING:** script utilizes python builtin module `shutil`. Moving files may cause loss of some metadata. See module's warning [here](https://docs.python.org/3/library/shutil.html).

## CSV Input File

If `-i` passed with input file path, then the script can import a list of patterns, and, if desired, a filter for file type extensions. See `inputFile.csv` in `/examples` for reference.

### File Columns

- **(required) 'pattern':** pattern values; supports unix-style pattern matching with '\*', etc.
- **(optional) 'extensions':** list of file types to filter matched files by
  - **note:** must include 'dot' ('.'), i.e. '.xlsx', '.png', etc.
  - **note:** 'extensions' column overrides exts passed at command line as arguments, but script will use command line arguments if no 'extensions' column in .csv

## Uses

Absolute paths (preferred):

`python matchcopy.py /source/absolute/path /destination/absolute/path -p match*this -e .txt`

Supports relative paths if script located in some top directory:

`python matchcopy.py ./source/relative/path ./destination/relative/path -p match*this -e .txt`

Multiple patterns and file extensions:

`python matchcopy.py /source/absolute/path /destination/absolute/path -p match*this and*also*this *why*not-a-third* -e .txt .png .exr`

Input file with explicit 'move' mode:

`python matchcopy.py /source/absolute/path /destination/absolute/path -i /path/to/inputFile.csv -m move`
