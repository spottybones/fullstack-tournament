# Swiss-System Tournament Library #
v1.0 January 19, 2016

## Description ##

This module provides a library of Python functions that can be used to
implement a simple [Swiss-system tournament][1].

## Requirements ##

This library requires that the following components be installed:

* Python v2.7 interpreter
* Psycopg2 Python module
* PostgreSQL database server

## File Manifest ##

The following files are included with this library:

* `tournament.py` - this file contains functions used to register players in a
  tournament, record results of matches played, and report player standings.

* `tournament_test.py` - a script that runs a series of tests to confirm that
  basic functionality is correctly implemented by the `tournament.py` library.

* `tournament.sql` - a SQL data definition language script that will initialize
  tables and views used by the library to persist tournament data.

## Installation ##

Perform the following steps to install this software:

1. Ensure the required Python interpreter, Psycopg2 module, and PostgreSQL
   database server are are installed and [initialized][2].

2. Clone the software repository:

   https://github.com/spottybones/fullstack-tournament

   to a directory on your system, or download the zip file and unzip it into an
   empty directory.

3. Change your working directory to the location of the tournament library
   file.

4. Create a new PostgreSQL database using the following command at a shell
   prompt:

   ```
   createdb tournament
   ```

5. Initialize the `tournament` database by entering the following at the shell
   prompt:

   ```
   psql -c "\i tournament.sql"
   ```

   Review the command output for errors. If any are found please open an
   [issue][3] with the library's Github repository.

## Running the tests ##

Tests for the `tournament.py` library are included in the `tournament_test.py`
script. Run it by entering:

```
python tournament_test.py
```

at the shell prompt. If any of the tests file please open an [issue][3] via the
repository.


[1]:https://en.wikipedia.org/wiki/Swiss-system_tournament
[2]:http://www.postgresql.org/docs/9.4/static/creating-cluster.html
[3]:https://github.com/spottybones/fullstack-tournament/issues
