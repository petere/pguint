SELECT '55'::int1;
SELECT '200'::int1;
SELECT ''::int1;
SELECT '-55'::int1;
SELECT '-200'::int1;

SELECT '55'::uint1;
SELECT '300'::uint1;
SELECT ''::uint1;
SELECT '-55'::uint1;

CREATE TABLE test1 (a int1, b uint1);

INSERT INTO test1 VALUES (-2, 1), (-1, 2), (0, 3), (1, 4), (2, 5);

SELECT a, b FROM test1;


SELECT '55'::uint2;
SELECT '70000'::uint2;
SELECT ''::uint2;
SELECT '-55'::uint2;


CREATE TABLE test2 (a uint2);

INSERT INTO test2 VALUES (1), (2), (3), (4), (5);

SELECT a FROM test2;


SELECT '55'::uint4;
SELECT ''::uint4;
SELECT '-55'::uint4;


CREATE TABLE test4 (a uint4);

INSERT INTO test4 VALUES (1), (2), (3), (4), (5);

SELECT a FROM test4;

SELECT avg(a) FROM test4;

SELECT sum(a) FROM test4;


SELECT '55'::uint8;
SELECT ''::uint8;
SELECT '-55'::uint8;


CREATE TABLE test8 (a uint8);

INSERT INTO test8 VALUES (1), (2), (3), (4), (5);

SELECT a FROM test8;
