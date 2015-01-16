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
