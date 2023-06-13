#include "rand64-sw.h"
#include <stdlib.h>
#include <time.h>

/* Software implementation.  */

/* Input stream containing random bytes.  */
FILE *urandstream;

/* Initialize the software rand64 implementation.  */
void
software_rand64_init (const char* file)
{
  if (file)
      urandstream = fopen (file, "r");
  if (! urandstream)
    abort ();
}

/* Return a random value, using software operations.  */
unsigned long long
software_rand64 (void)
{
  unsigned long long int x;
  if (fread (&x, sizeof x, 1, urandstream) != 1)
    abort ();
  return x;
}

/* Finalize the software rand64 implementation.  */
void
software_rand64_fini (void)
{
  fclose (urandstream);
}

/* Initialize the mrand48_r rand64 implementation.  */
void
mrand48_rand64_init ([[maybe_unused]] const char* file)
{
 
}

/* Return a random value, using mrand48_r operations.  */
unsigned long long
mrand48_rand64 (void)
{
  long int result;
  struct drand48_data buffer;
  srand48_r(time(NULL), &buffer);  //Seed with current time
  mrand48_r(&buffer, &result);    //Generate random number
  return (unsigned long long) result;
}

/* Finalize the mrand48_r rand64 implementation.  */
void
mrand48_rand64_fini (void)
{
  
}
