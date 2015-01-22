#include <postgres.h>
#include <fmgr.h>

#define DatumGetInt8(X)		((int8) GET_1_BYTE(X))  /* XXX */
#define DatumGetUInt64(X)	((uint64) GET_8_BYTES(X))
#define UInt64GetDatum(X)	((Datum) SET_8_BYTES(X))

#define PG_GETARG_INT8(n)	DatumGetInt8(PG_GETARG_DATUM(n))
#define PG_RETURN_INT8(x)	return Int8GetDatum(x)
#define PG_GETARG_UINT8(n)	DatumGetUInt8(PG_GETARG_DATUM(n))
#define PG_RETURN_UINT8(x)	return UInt8GetDatum(x)
#ifndef PG_RETURN_UINT16
#define PG_RETURN_UINT16(x)	return UInt16GetDatum(x)
#endif
#define PG_GETARG_UINT64(n)	DatumGetUInt64(PG_GETARG_DATUM(n))
#define PG_RETURN_UINT64(x)	return UInt64GetDatum(x)
