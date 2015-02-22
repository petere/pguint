Unsigned and other extra integer types for PostgreSQL
=====================================================

This extension provides additional integer types for PostgreSQL:

- `int1` (signed 8-bit integer)
- `uint1` (unsigned 8-bit integer)
- `uint2` (unsigned 16-bit integer)
- `uint4` (unsigned 32-bit integer)
- `uint8` (unsigned 64-bit integer)

Installation
------------

PostgreSQL version 9.1 or later is required.

To build and install this module:

    make
    make install

or selecting a specific PostgreSQL installation:

    make PG_CONFIG=/some/where/bin/pg_config
    make PG_CONFIG=/some/where/bin/pg_config install

And finally inside the database:

    CREATE EXTENSION uint;

Using
-----

You can use the new types like the standard integer types.  Examples:

```sql
CREATE TABLE foo (
    a uint4,
    b text
);

SELECT * FROM foo WHERE a > 4;

SELECT avg(a) FROM foo;
```

The types come with a sizable set of operators and functions, index
support, etc.  Some pieces are still missing, but they are being
worked on.  If there is anything you can't find, let me know.

Discussion
----------

Support for unsigned integer types and smaller integer types has been
one of the more common outstanding feature request for PostgreSQL.
Inclusion of additional integer types into the core is typically
rejected with the argument that it would make the type system too
complicated and fragile.  The experience from writing this module
suggests: That is not wrong.  Another argument, either explicit or
implicit, is that it is a lot of work.  Again: true.

The combination of the requirements of the SQL standard and the type
system of PostgreSQL effectively create a situation where you need to
provide a comprehensive set of operators and functions for *each
combination* of numeric types.  So for the three standard integer
types, that's 9 "+" operators, 9 "<" operators, and so on.  And with
3 + 5 = 8 types, well, you do the math.  This module solves that
problem by generating most of the code automatically.

The purpose of this module is therefore twofold: First, it should be
useful in practice.  There is no reason why it couldn't be.  Second,
it is a challenge to the PostgreSQL extension mechanism.  In that
area, there are various "interesting" problems that still need to be
worked out.

Testing
-------

In addition to the test suite of this module (`make installcheck`), it
is useful to test this module by running the main PostgreSQL
regression tests while this module is loaded, which should not fail.
This will verify that the presence of the additional types and
operators will not cause changes in the interpretation of expressions
involving the existing types and operators.
