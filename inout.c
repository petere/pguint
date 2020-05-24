#include <postgres.h>
#include <libpq/pqformat.h>
#include <fmgr.h>
#include <utils/builtins.h>

#include "uint.h"

#include <inttypes.h>
#include <limits.h>


PG_FUNCTION_INFO_V1(int1in);
Datum
int1in(PG_FUNCTION_ARGS)
{
	char	   *s = PG_GETARG_CSTRING(0);

	PG_RETURN_INT8(pg_atoi(s, sizeof(int8), '\0'));
}

PG_FUNCTION_INFO_V1(int1out);
Datum
int1out(PG_FUNCTION_ARGS)
{
	int8		arg1 = PG_GETARG_INT8(0);
	char	   *result = palloc(5);		/* sign, 3 digits, '\0' */

	sprintf(result, "%d", arg1);
	PG_RETURN_CSTRING(result);
}

static uint32
pg_atou(const char *s, int size)
{
	unsigned long int result;
	bool		out_of_range = false;
	char	   *badp;

	if (s == NULL)
		elog(ERROR, "NULL pointer");
	if (*s == 0)
		ereport(ERROR,
				(errcode(ERRCODE_INVALID_TEXT_REPRESENTATION),
				 errmsg("invalid input syntax for unsigned integer: \"%s\"",
						s)));

	if (strchr(s, '-'))
		ereport(ERROR,
				(errcode(ERRCODE_INVALID_TEXT_REPRESENTATION),
				 errmsg("invalid input syntax for unsigned integer: \"%s\"",
						s)));

	errno = 0;
	result = strtoul(s, &badp, 10);

	switch (size)
	{
		case sizeof(uint32):
			if (errno == ERANGE
#if defined(HAVE_LONG_INT_64)
				|| result > UINT_MAX
				#endif
				)
				out_of_range = true;
			break;
		case sizeof(uint16):
			if (errno == ERANGE || result > USHRT_MAX)
				out_of_range = true;
			break;
		case sizeof(uint8):
			if (errno == ERANGE || result > UCHAR_MAX)
				out_of_range = true;
			break;
		default:
			elog(ERROR, "unsupported result size: %d", size);
	}

	if (out_of_range)
		ereport(ERROR,
				(errcode(ERRCODE_NUMERIC_VALUE_OUT_OF_RANGE),
				 errmsg("value \"%s\" is out of range for type uint%d", s, size)));

	while (*badp && isspace((unsigned char) *badp))
		badp++;

	if (*badp)
		ereport(ERROR,
				(errcode(ERRCODE_INVALID_TEXT_REPRESENTATION),
				 errmsg("invalid input syntax for unsigned integer: \"%s\"",
						s)));

	return result;
}

PG_FUNCTION_INFO_V1(uint1in);
Datum
uint1in(PG_FUNCTION_ARGS)
{
	char	   *s = PG_GETARG_CSTRING(0);

	PG_RETURN_UINT8(pg_atou(s, sizeof(uint8)));
}

PG_FUNCTION_INFO_V1(uint1out);
Datum
uint1out(PG_FUNCTION_ARGS)
{
	uint8		arg1 = PG_GETARG_UINT8(0);
	char	   *result = palloc(4);		/* 3 digits, '\0' */

	sprintf(result, "%u", arg1);
	PG_RETURN_CSTRING(result);
}

PG_FUNCTION_INFO_V1(uint2in);
Datum
uint2in(PG_FUNCTION_ARGS)
{
	char	   *s = PG_GETARG_CSTRING(0);

	PG_RETURN_UINT16(pg_atou(s, sizeof(uint16)));
}

PG_FUNCTION_INFO_V1(uint2out);
Datum
uint2out(PG_FUNCTION_ARGS)
{
	uint16		arg1 = PG_GETARG_UINT16(0);
	char	   *result = palloc(6);		/* 5 digits, '\0' */

	sprintf(result, "%u", arg1);
	PG_RETURN_CSTRING(result);
}

PG_FUNCTION_INFO_V1(uint4in);
Datum
uint4in(PG_FUNCTION_ARGS)
{
	char	   *s = PG_GETARG_CSTRING(0);

	PG_RETURN_UINT32(pg_atou(s, sizeof(uint32)));
}

PG_FUNCTION_INFO_V1(uint4out);
Datum
uint4out(PG_FUNCTION_ARGS)
{
	uint32		arg1 = PG_GETARG_UINT32(0);
	char	   *result = palloc(11);	/* 10 digits, '\0' */

	sprintf(result, "%u", arg1);
	PG_RETURN_CSTRING(result);
}

PG_FUNCTION_INFO_V1(uint8in);
Datum
uint8in(PG_FUNCTION_ARGS)
{
	char	   *s = PG_GETARG_CSTRING(0);
	unsigned long long int result;
	char	   *badp;

	if (s == NULL)
		elog(ERROR, "NULL pointer");
	if (*s == 0)
		ereport(ERROR,
				(errcode(ERRCODE_INVALID_TEXT_REPRESENTATION),
				 errmsg("invalid input syntax for unsigned integer: \"%s\"",
						s)));

	if (strchr(s, '-'))
		ereport(ERROR,
				(errcode(ERRCODE_INVALID_TEXT_REPRESENTATION),
				 errmsg("invalid input syntax for unsigned integer: \"%s\"",
						s)));

	errno = 0;
	result = strtoull(s, &badp, 10);

	if (errno == ERANGE)
		ereport(ERROR,
				(errcode(ERRCODE_NUMERIC_VALUE_OUT_OF_RANGE),
				 errmsg("value \"%s\" is out of range for type uint%d", s, 8)));

	while (*badp && isspace((unsigned char) *badp))
		badp++;

	if (*badp)
		ereport(ERROR,
				(errcode(ERRCODE_INVALID_TEXT_REPRESENTATION),
				 errmsg("invalid input syntax for unsigned integer: \"%s\"",
						s)));

	PG_RETURN_UINT64(result);
}

PG_FUNCTION_INFO_V1(uint8out);
Datum
uint8out(PG_FUNCTION_ARGS)
{
	uint64		arg1 = PG_GETARG_UINT64(0);
	char	   *result = palloc(21);	/* 20 digits, '\0' */

	sprintf(result, "%"PRIu64, (uint64_t) arg1);
	PG_RETURN_CSTRING(result);
}

PG_FUNCTION_INFO_V1(int1recv);
Datum
int1recv(PG_FUNCTION_ARGS)
{
    StringInfo  buf = (StringInfo) PG_GETARG_POINTER(0);
    PG_RETURN_INT8((int8) pq_getmsgint(buf, sizeof(int8)));
}

PG_FUNCTION_INFO_V1(int1send);
Datum
int1send(PG_FUNCTION_ARGS)
{
    int8       arg1 = PG_GETARG_INT8(0);
    StringInfoData buf;

    pq_begintypsend(&buf);
    pq_sendint(&buf, arg1, sizeof(int8));
    PG_RETURN_BYTEA_P(pq_endtypsend(&buf));
}

PG_FUNCTION_INFO_V1(uint1recv);
Datum
uint1recv(PG_FUNCTION_ARGS)
{
    StringInfo  buf = (StringInfo) PG_GETARG_POINTER(0);
    PG_RETURN_UINT8((uint8) pq_getmsgint(buf, sizeof(uint8)));
}

PG_FUNCTION_INFO_V1(uint1send);
Datum
uint1send(PG_FUNCTION_ARGS)
{
    uint8       arg1 = PG_GETARG_UINT8(0);
    StringInfoData buf;

    pq_begintypsend(&buf);
    pq_sendint(&buf, arg1, sizeof(uint8));
    PG_RETURN_BYTEA_P(pq_endtypsend(&buf));
}

PG_FUNCTION_INFO_V1(uint2recv);
Datum
uint2recv(PG_FUNCTION_ARGS)
{
    StringInfo  buf = (StringInfo) PG_GETARG_POINTER(0);
    PG_RETURN_UINT16((uint16) pq_getmsgint(buf, sizeof(uint16)));
}

PG_FUNCTION_INFO_V1(uint2send);
Datum
uint2send(PG_FUNCTION_ARGS)
{
    uint16      arg1 = PG_GETARG_UINT16(0);
    StringInfoData buf;

    pq_begintypsend(&buf);
    pq_sendint(&buf, arg1, sizeof(uint16));
    PG_RETURN_BYTEA_P(pq_endtypsend(&buf));
}

PG_FUNCTION_INFO_V1(uint4recv);
Datum
uint4recv(PG_FUNCTION_ARGS)
{
    StringInfo  buf = (StringInfo) PG_GETARG_POINTER(0);
    PG_RETURN_UINT32((uint32) pq_getmsgint(buf, sizeof(uint32)));
}

PG_FUNCTION_INFO_V1(uint4send);
Datum
uint4send(PG_FUNCTION_ARGS)
{
    uint32      arg1 = PG_GETARG_UINT32(0);
    StringInfoData buf;

    pq_begintypsend(&buf);
    pq_sendint(&buf, arg1, sizeof(uint32));
    PG_RETURN_BYTEA_P(pq_endtypsend(&buf));
}

PG_FUNCTION_INFO_V1(uint8recv);
Datum
uint8recv(PG_FUNCTION_ARGS)
{
    StringInfo  buf = (StringInfo) PG_GETARG_POINTER(0);
    PG_RETURN_UINT64((uint64) pq_getmsgint64(buf));
}

PG_FUNCTION_INFO_V1(uint8send);
Datum
uint8send(PG_FUNCTION_ARGS)
{
    uint64      arg1 = PG_GETARG_UINT64(0);
    StringInfoData buf;

    pq_begintypsend(&buf);
    pq_sendint64(&buf, arg1);
    PG_RETURN_BYTEA_P(pq_endtypsend(&buf));
}
