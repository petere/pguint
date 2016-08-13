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

CREATE TYPE int1 (
    INPUT = int1in,
    OUTPUT = int1out,
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

CREATE TYPE uint1 (
    INPUT = uint1in,
    OUTPUT = uint1out,
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

CREATE TYPE uint2 (
    INPUT = uint2in,
    OUTPUT = uint2out,
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

CREATE TYPE uint4 (
    INPUT = uint4in,
    OUTPUT = uint4out,
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

CREATE TYPE uint8 (
    INPUT = uint8in,
    OUTPUT = uint8out,
    INTERNALLENGTH = 8,
    @UINT8_PASSEDBYVALUE@
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
