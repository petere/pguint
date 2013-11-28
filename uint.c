#include <postgres.h>
#include <fmgr.h>

#include <utils/array.h>
#include <utils/builtins.h>


PG_MODULE_MAGIC;

PG_FUNCTION_INFO_V1(uint4in);
PG_FUNCTION_INFO_V1(uint4out);
PG_FUNCTION_INFO_V1(uint4_avg_accum);
PG_FUNCTION_INFO_V1(int8_avg);

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

typedef struct Int8TransTypeData
{
	int64		count;
	int64		sum;
} Int8TransTypeData;

Datum
uint4_avg_accum(PG_FUNCTION_ARGS)
{
	ArrayType  *transarray;
	uint32		newval = PG_GETARG_UINT32(1);
	Int8TransTypeData *transdata;

	/*
	 * If we're invoked as an aggregate, we can cheat and modify our first
	 * parameter in-place to reduce palloc overhead. Otherwise we need to make
	 * a copy of it before scribbling on it.
	 */
	if (AggCheckCallContext(fcinfo, NULL))
		transarray = PG_GETARG_ARRAYTYPE_P(0);
	else
		transarray = PG_GETARG_ARRAYTYPE_P_COPY(0);

	if (ARR_HASNULL(transarray) ||
		ARR_SIZE(transarray) != ARR_OVERHEAD_NONULLS(1) + sizeof(Int8TransTypeData))
		elog(ERROR, "expected 2-element int8 array");

	transdata = (Int8TransTypeData *) ARR_DATA_PTR(transarray);
	transdata->count++;
	transdata->sum += newval;

	PG_RETURN_ARRAYTYPE_P(transarray);
}

Datum
int8_avg(PG_FUNCTION_ARGS)
{
	ArrayType  *transarray = PG_GETARG_ARRAYTYPE_P(0);
	Int8TransTypeData *transdata;
	Datum		countd,
				sumd;

	if (ARR_HASNULL(transarray) ||
		ARR_SIZE(transarray) != ARR_OVERHEAD_NONULLS(1) + sizeof(Int8TransTypeData))
		elog(ERROR, "expected 2-element int8 array");
	transdata = (Int8TransTypeData *) ARR_DATA_PTR(transarray);

	/* SQL defines AVG of no values to be NULL */
	if (transdata->count == 0)
		PG_RETURN_NULL();

	countd = DirectFunctionCall1(int8_numeric,
								 Int64GetDatumFast(transdata->count));
	sumd = DirectFunctionCall1(int8_numeric,
							   Int64GetDatumFast(transdata->sum));

	PG_RETURN_DATUM(DirectFunctionCall2(numeric_div, sumd, countd));
}
