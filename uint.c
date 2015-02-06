#include <postgres.h>
#include <fmgr.h>

#include "uint.h"

#include <inttypes.h>
#include <limits.h>


PG_MODULE_MAGIC;

PG_FUNCTION_INFO_V1(int1in);
PG_FUNCTION_INFO_V1(int1out);
PG_FUNCTION_INFO_V1(uint1in);
PG_FUNCTION_INFO_V1(uint1out);
PG_FUNCTION_INFO_V1(uint2in);
PG_FUNCTION_INFO_V1(uint2out);
PG_FUNCTION_INFO_V1(uint4in);
PG_FUNCTION_INFO_V1(uint4out);
PG_FUNCTION_INFO_V1(uint8in);
PG_FUNCTION_INFO_V1(uint8out);
PG_FUNCTION_INFO_V1(int1um);


Datum
int1in(PG_FUNCTION_ARGS)
{
	char	   *s = PG_GETARG_CSTRING(0);
	long int	result;

	if (s == NULL)
		elog(ERROR, "NULL pointer");
	if (*s == 0)
		ereport(ERROR,
				(errcode(ERRCODE_INVALID_TEXT_REPRESENTATION),
				 errmsg("invalid input syntax for integer: \"%s\"",
						s)));

	errno = 0;
	result = strtol(s, NULL, 10);
	if (errno == ERANGE || result > SCHAR_MAX || result < SCHAR_MIN)
		ereport(ERROR,
				(errcode(ERRCODE_NUMERIC_VALUE_OUT_OF_RANGE),
				 errmsg("value \"%s\" is out of range for type int1", s)));

	PG_RETURN_INT8(result);
}

Datum
int1out(PG_FUNCTION_ARGS)
{
	int8		arg1 = PG_GETARG_INT8(0);
	char	   *result = (char *) palloc(11);	/* 10 digits, '\0' */

	sprintf(result, "%d", arg1);
	PG_RETURN_CSTRING(result);
}

Datum
uint1in(PG_FUNCTION_ARGS)
{
	char	   *s = PG_GETARG_CSTRING(0);
	unsigned long int result;

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
	result = strtoul(s, NULL, 10);
	if (errno == ERANGE || result > UCHAR_MAX)
		ereport(ERROR,
				(errcode(ERRCODE_NUMERIC_VALUE_OUT_OF_RANGE),
				 errmsg("value \"%s\" is out of range for type uint1", s)));

	PG_RETURN_UINT8(result);
}

Datum
uint1out(PG_FUNCTION_ARGS)
{
	uint8		arg1 = PG_GETARG_UINT8(0);
	char	   *result = (char *) palloc(11);	/* 10 digits, '\0' */

	sprintf(result, "%u", arg1);
	PG_RETURN_CSTRING(result);
}

Datum
uint2in(PG_FUNCTION_ARGS)
{
	char	   *s = PG_GETARG_CSTRING(0);
	unsigned long int result;

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
	result = strtoul(s, NULL, 10);
	if (errno == ERANGE || result > USHRT_MAX)
		ereport(ERROR,
				(errcode(ERRCODE_NUMERIC_VALUE_OUT_OF_RANGE),
				 errmsg("value \"%s\" is out of range for type uint2", s)));

	PG_RETURN_UINT16(result);
}

Datum
uint2out(PG_FUNCTION_ARGS)
{
	uint16		arg1 = PG_GETARG_UINT16(0);
	char	   *result = (char *) palloc(11);	/* 10 digits, '\0' */

	sprintf(result, "%u", arg1);
	PG_RETURN_CSTRING(result);
}

Datum
uint4in(PG_FUNCTION_ARGS)
{
	char	   *s = PG_GETARG_CSTRING(0);
	unsigned long int result;

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

	result = strtoul(s, NULL, 10);

	PG_RETURN_UINT32(result);
}

Datum
uint4out(PG_FUNCTION_ARGS)
{
	uint32		arg1 = PG_GETARG_UINT32(0);
	char	   *result = (char *) palloc(11);	/* 10 digits, '\0' */

	sprintf(result, "%u", arg1);
	PG_RETURN_CSTRING(result);
}

Datum
uint8in(PG_FUNCTION_ARGS)
{
	char	   *s = PG_GETARG_CSTRING(0);
	unsigned long long int result;

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

	result = strtoull(s, NULL, 10);

	PG_RETURN_UINT64(result);
}

Datum
uint8out(PG_FUNCTION_ARGS)
{
	uint64		arg1 = PG_GETARG_UINT64(0);
	char	   *result = (char *) palloc(21);	/* 20 digits, '\0' */

	sprintf(result, "%"PRIu64, arg1);
	PG_RETURN_CSTRING(result);
}

Datum
int1um(PG_FUNCTION_ARGS)
{
	int8		arg = PG_GETARG_INT8(0);
	int8		result;

	result = -arg;
	/* overflow check */
	if (arg != 0 && SAMESIGN(result, arg))
		ereport(ERROR,
				(errcode(ERRCODE_NUMERIC_VALUE_OUT_OF_RANGE),
				 errmsg("integer out of range")));
	PG_RETURN_INT8(result);
}
