-- Test extension upgrade from version 0 to 1
-- Version 0 has the types without binary I/O
-- Version 1 adds the binary send/recv functions

-- Start with version 0
CREATE EXTENSION uint VERSION '0';

-- Test that types work
SELECT 42::uint4;
SELECT 255::uint1;

-- Verify binary functions don't exist yet
\df uint1send
\df uint1recv

-- Upgrade to version 1
ALTER EXTENSION uint UPDATE TO '1';

-- Verify binary functions now exist
\df uint1send
\df uint1recv

-- Test binary protocol functions work
SELECT encode(uint1send(255::uint1), 'hex');
SELECT encode(uint4send(4294967295::uint4), 'hex');

-- Test roundtrip through binary format
CREATE TEMP TABLE upgrade_test (
    u1 uint1,
    u4 uint4
);

INSERT INTO upgrade_test VALUES (128, 2147483648);

-- Use COPY to test binary I/O
COPY upgrade_test TO '/tmp/upgrade_test.dat' WITH (FORMAT binary);
DELETE FROM upgrade_test;
COPY upgrade_test FROM '/tmp/upgrade_test.dat' WITH (FORMAT binary);

SELECT * FROM upgrade_test;

DROP TABLE upgrade_test;