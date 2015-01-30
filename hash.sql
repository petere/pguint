CREATE FUNCTION hashint1(int1) RETURNS int4 IMMUTABLE STRICT LANGUAGE C AS '$libdir/uint', 'hashint1';
CREATE FUNCTION hashuint1(uint1) RETURNS int4 IMMUTABLE STRICT LANGUAGE C AS '$libdir/uint', 'hashuint1';
CREATE FUNCTION hashuint2(uint2) RETURNS int4 IMMUTABLE STRICT LANGUAGE C AS '$libdir/uint', 'hashuint2';
CREATE FUNCTION hashuint4(uint4) RETURNS int4 IMMUTABLE STRICT LANGUAGE C AS '$libdir/uint', 'hashuint4';
CREATE FUNCTION hashuint8(uint8) RETURNS int4 IMMUTABLE STRICT LANGUAGE C AS '$libdir/uint', 'hashuint8';
