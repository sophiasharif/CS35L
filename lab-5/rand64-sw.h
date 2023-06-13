#ifndef RAND64_SW
#define RAND64_SW

#include <stdio.h>

/* Initialize the software rand64 implementation.  */
void software_rand64_init (const char* file);

/* Return a random value, using software operations.  */
unsigned long long software_rand64 (void);

/* Finalize the software rand64 implementation.  */
void software_rand64_fini (void);

/* Initialize the mrand48_r rand64 implementation.  */
void mrand48_rand64_init ([[maybe_unused]] const char* file);

/* Return a random value, using mrand48_r operations.  */
unsigned long long mrand48_rand64 (void);

/* Finalize the mrand48_r rand64 implementation.  */
void mrand48_rand64_fini (void);

#endif
