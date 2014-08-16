CREATE TYPE uint4;

CREATE FUNCTION uint4in(cstring) RETURNS uint4
    LANGUAGE C
    AS '$libdir/uint', 'uint4in';

CREATE FUNCTION uint4out(uint4) RETURNS cstring
    LANGUAGE C
    AS '$libdir/uint', 'uint4out';

CREATE TYPE uint4 (
    INPUT = uint4in,
    OUTPUT = uint4out,
    INTERNALLENGTH = 4,
    PASSEDBYVALUE,
    ALIGNMENT = int4
);

CREATE CAST (bigint AS uint4) WITH INOUT AS ASSIGNMENT;
CREATE CAST (int AS uint4) WITH INOUT AS ASSIGNMENT;
CREATE CAST (double precision AS uint4) WITH INOUT AS ASSIGNMENT;
CREATE CAST (numeric AS uint4) WITH INOUT AS ASSIGNMENT;
CREATE CAST (oid AS uint4) WITH INOUT AS ASSIGNMENT;
CREATE CAST (real AS uint4) WITH INOUT AS ASSIGNMENT;
CREATE CAST (smallint AS uint4) WITH INOUT AS IMPLICIT;

CREATE CAST (uint4 AS bigint) WITH INOUT AS IMPLICIT;
CREATE CAST (uint4 AS double precision) WITH INOUT AS IMPLICIT;
CREATE CAST (uint4 AS money) WITH INOUT AS ASSIGNMENT;
CREATE CAST (uint4 AS numeric) WITH INOUT AS IMPLICIT;
CREATE CAST (uint4 AS oid) WITH INOUT AS IMPLICIT;
CREATE CAST (uint4 AS real) WITH INOUT AS IMPLICIT;
CREATE CAST (uint4 AS smallint) WITH INOUT AS ASSIGNMENT;


CREATE FUNCTION uint4_avg_accum(_int8, uint4) RETURNS _int8
    STRICT IMMUTABLE
    LANGUAGE C
    AS '$libdir/uint', 'uint4_avg_accum';

CREATE FUNCTION uint4_sum(int8, uint4) RETURNS int8
    IMMUTABLE
    LANGUAGE C
    AS '$libdir/uint', 'uint4_sum';

CREATE AGGREGATE avg(uint4) (
    SFUNC = uint4_avg_accum,
    STYPE = _int8,
    FINALFUNC = int8_avg,
    INITCOND = '{0,0}'
);

CREATE AGGREGATE sum(uint4) (
    SFUNC = uint4_sum,
    STYPE = int8
);
