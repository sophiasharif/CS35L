#ifndef RAND64_HW
#define RAND64_HW

/* Return true if the CPU supports the RDRAND instruction.  */
_Bool rdrand_supported (void);

/* Initialize the hardware rand64 implementation.  */
void hardware_rand64_init (const char* file);

/* Return a random value, using hardware operations.  */
unsigned long long hardware_rand64 (void);

/* Finalize the hardware rand64 implementation.  */
void hardware_rand64_fini (void);

#endif
