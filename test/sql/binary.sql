-- Test binary I/O functions
-- Note: recv functions cannot be called directly in SQL
-- We'll test them via casts instead

-- int1
SELECT encode(int1send((-128)::int1), 'hex');
SELECT encode(int1send(0::int1), 'hex');
SELECT encode(int1send(127::int1), 'hex');

-- uint1
SELECT encode(uint1send(0::uint1), 'hex');
SELECT encode(uint1send(255::uint1), 'hex');

-- uint2
SELECT encode(uint2send(0::uint2), 'hex');
SELECT encode(uint2send(65535::uint2), 'hex');

-- uint4
SELECT encode(uint4send(0::uint4), 'hex');
SELECT encode(uint4send(4294967295::uint4), 'hex');

-- uint8
SELECT encode(uint8send(0::uint8), 'hex');
SELECT encode(uint8send(18446744073709551615::uint8), 'hex');

-- Test roundtrip via binary copy
CREATE TEMP TABLE test_binary (
    i1 int1,
    u1 uint1,
    u2 uint2,
    u4 uint4,
    u8 uint8
);

INSERT INTO test_binary VALUES (-128, 0, 0, 0, 0);
INSERT INTO test_binary VALUES (0, 128, 32768, 2147483648, 9223372036854775808);
INSERT INTO test_binary VALUES (127, 255, 65535, 4294967295, 18446744073709551615);

-- Binary copy out and back in to test send/recv functions
COPY test_binary TO '/tmp/test_binary.dat' WITH (FORMAT binary);
DELETE FROM test_binary;
COPY test_binary FROM '/tmp/test_binary.dat' WITH (FORMAT binary);

SELECT * FROM test_binary ORDER BY i1;
