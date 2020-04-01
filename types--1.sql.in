CREATE TYPE int1;

CREATE FUNCTION int1in(cstring) RETURNS int1
    IMMUTABLE
    STRICT
    LANGUAGE C
    AS '$libdir/uint', 'int1in';

CREATE FUNCTION int1out(int1) RETURNS cstring
    IMMUTABLE
    STRICT
    LANGUAGE C
    AS '$libdir/uint', 'int1out';

CREATE FUNCTION int1recv(internal) RETURNS int1
    IMMUTABLE
    STRICT
    LANGUAGE C
    AS '$libdir/uint', 'int1recv';

CREATE FUNCTION int1send(int1) RETURNS bytea
    IMMUTABLE
    STRICT
    LANGUAGE C
    AS '$libdir/uint', 'int1send';


CREATE TYPE int1 (
    INPUT = int1in,
    OUTPUT = int1out,
    RECEIVE = int1recv,
    SEND = int1send,
    INTERNALLENGTH = 1,
    PASSEDBYVALUE,
    ALIGNMENT = char
);

CREATE CAST (double precision AS int1) WITH INOUT AS ASSIGNMENT;
CREATE CAST (numeric AS int1) WITH INOUT AS ASSIGNMENT;
CREATE CAST (real AS int1) WITH INOUT AS ASSIGNMENT;

CREATE CAST (int1 AS double precision) WITH INOUT AS IMPLICIT;
CREATE CAST (int1 AS numeric) WITH INOUT AS IMPLICIT;
CREATE CAST (int1 AS real) WITH INOUT AS IMPLICIT;


CREATE TYPE uint1;

CREATE FUNCTION uint1in(cstring) RETURNS uint1
    IMMUTABLE
    STRICT
    LANGUAGE C
    AS '$libdir/uint', 'uint1in';

CREATE FUNCTION uint1out(uint1) RETURNS cstring
    IMMUTABLE
    STRICT
    LANGUAGE C
    AS '$libdir/uint', 'uint1out';

CREATE FUNCTION uint1recv(internal) RETURNS uint1
    IMMUTABLE
    STRICT
    LANGUAGE C
    AS '$libdir/uint', 'uint1recv';

CREATE FUNCTION uint1send(uint1) RETURNS bytea
    IMMUTABLE
    STRICT
    LANGUAGE C
    AS '$libdir/uint', 'uint1send';

CREATE TYPE uint1 (
    INPUT = uint1in,
    OUTPUT = uint1out,
    RECEIVE = uint1recv,
    SEND = uint1send,
    INTERNALLENGTH = 1,
    PASSEDBYVALUE,
    ALIGNMENT = char
);

CREATE CAST (double precision AS uint1) WITH INOUT AS ASSIGNMENT;
CREATE CAST (numeric AS uint1) WITH INOUT AS ASSIGNMENT;
CREATE CAST (real AS uint1) WITH INOUT AS ASSIGNMENT;

CREATE CAST (uint1 AS double precision) WITH INOUT AS IMPLICIT;
CREATE CAST (uint1 AS numeric) WITH INOUT AS IMPLICIT;
CREATE CAST (uint1 AS real) WITH INOUT AS IMPLICIT;


CREATE TYPE uint2;

CREATE FUNCTION uint2in(cstring) RETURNS uint2
    IMMUTABLE
    STRICT
    LANGUAGE C
    AS '$libdir/uint', 'uint2in';

CREATE FUNCTION uint2out(uint2) RETURNS cstring
    IMMUTABLE
    STRICT
    LANGUAGE C
    AS '$libdir/uint', 'uint2out';

CREATE FUNCTION uint2recv(internal) RETURNS uint2
    IMMUTABLE
    STRICT
    LANGUAGE C
    AS '$libdir/uint', 'uint2recv';

CREATE FUNCTION uint2send(uint2) RETURNS bytea
    IMMUTABLE
    STRICT
    LANGUAGE C
    AS '$libdir/uint', 'uint2send';

CREATE TYPE uint2 (
    INPUT = uint2in,
    OUTPUT = uint2out,
    RECEIVE = uint2recv,
    SEND = uint2send,
    INTERNALLENGTH = 2,
    PASSEDBYVALUE,
    ALIGNMENT = int2
);

CREATE CAST (double precision AS uint2) WITH INOUT AS ASSIGNMENT;
CREATE CAST (numeric AS uint2) WITH INOUT AS ASSIGNMENT;
CREATE CAST (real AS uint2) WITH INOUT AS ASSIGNMENT;

CREATE CAST (uint2 AS double precision) WITH INOUT AS IMPLICIT;
CREATE CAST (uint2 AS numeric) WITH INOUT AS IMPLICIT;
CREATE CAST (uint2 AS real) WITH INOUT AS IMPLICIT;


CREATE TYPE uint4;

CREATE FUNCTION uint4in(cstring) RETURNS uint4
    IMMUTABLE
    STRICT
    LANGUAGE C
    AS '$libdir/uint', 'uint4in';

CREATE FUNCTION uint4out(uint4) RETURNS cstring
    IMMUTABLE
    STRICT
    LANGUAGE C
    AS '$libdir/uint', 'uint4out';

CREATE FUNCTION uint4recv(internal) RETURNS uint4
    IMMUTABLE
    STRICT
    LANGUAGE C
    AS '$libdir/uint', 'uint4recv';

CREATE FUNCTION uint4send(uint4) RETURNS bytea
    IMMUTABLE
    STRICT
    LANGUAGE C
    AS '$libdir/uint', 'uint4send';

CREATE TYPE uint4 (
    INPUT = uint4in,
    OUTPUT = uint4out,
    RECEIVE = uint4recv,
    SEND = uint4send,
    INTERNALLENGTH = 4,
    PASSEDBYVALUE,
    ALIGNMENT = int4
);

CREATE CAST (double precision AS uint4) WITH INOUT AS ASSIGNMENT;
CREATE CAST (numeric AS uint4) WITH INOUT AS ASSIGNMENT;
CREATE CAST (real AS uint4) WITH INOUT AS ASSIGNMENT;

CREATE CAST (uint4 AS double precision) WITH INOUT AS IMPLICIT;
CREATE CAST (uint4 AS numeric) WITH INOUT AS IMPLICIT;
CREATE CAST (uint4 AS real) WITH INOUT AS IMPLICIT;


CREATE TYPE uint8;

CREATE FUNCTION uint8in(cstring) RETURNS uint8
    IMMUTABLE
    STRICT
    LANGUAGE C
    AS '$libdir/uint', 'uint8in';

CREATE FUNCTION uint8out(uint8) RETURNS cstring
    IMMUTABLE
    STRICT
    LANGUAGE C
    AS '$libdir/uint', 'uint8out';

CREATE FUNCTION uint8recv(internal) RETURNS uint8
    IMMUTABLE
    STRICT
    LANGUAGE C
    AS '$libdir/uint', 'uint8recv';

CREATE FUNCTION uint8send(uint8) RETURNS bytea
    IMMUTABLE
    STRICT
    LANGUAGE C
    AS '$libdir/uint', 'uint8send';

CREATE TYPE uint8 (
    INPUT = uint8in,
    OUTPUT = uint8out,
    RECEIVE = uint8recv,
    SEND = uint8send,
    INTERNALLENGTH = 8,
    PASSEDBYVALUE,  -- requires 64-bit
    ALIGNMENT = double
);

CREATE CAST (double precision AS uint8) WITH INOUT AS ASSIGNMENT;
CREATE CAST (numeric AS uint8) WITH INOUT AS ASSIGNMENT;
CREATE CAST (real AS uint8) WITH INOUT AS ASSIGNMENT;

CREATE CAST (uint8 AS double precision) WITH INOUT AS IMPLICIT;
CREATE CAST (uint8 AS numeric) WITH INOUT AS IMPLICIT;
CREATE CAST (uint8 AS real) WITH INOUT AS IMPLICIT;


CREATE FUNCTION int1um(int1) RETURNS int1 IMMUTABLE STRICT LANGUAGE C AS '$libdir/uint', 'int1um';

CREATE OPERATOR - (
   PROCEDURE = int1um,
   RIGHTARG = int1
);
