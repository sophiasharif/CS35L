/* Generate N bytes of random output.  */

/* When generating output this program uses the x86-64 RDRAND
   instruction if available to generate random numbers, falling back
   on /dev/random and stdio otherwise.

   This program is not portable.  Compile it with gcc -mrdrnd for a
   x86-64 machine.

   Copyright 2015, 2017, 2020 Paul Eggert

   This program is free software: you can redistribute it and/or
   modify it under the terms of the GNU General Public License as
   published by the Free Software Foundation, either version 3 of the
   License, or (at your option) any later version.

   This program is distributed in the hope that it will be useful, but
   WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
   General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.  */

#include <errno.h>
#include <stdbool.h>
#include <stdlib.h>
#include <unistd.h>
#include <ctype.h>
#include <string.h>

#include "rand64-hw.h"
#include "rand64-sw.h"
#include "output.h"
#include "options.h"

/* Main program, which outputs N bytes of random data.  */
int main(int argc, char **argv)
{
  struct options opts;
  opts.input = NULL;
  opts.output_method = NULL;
  opts.block_size = 0;
  opts.nbytes = 0;


  if (parse_options(argc, argv, &opts) != 0)
    return 1;
  
  /* If there's no work to do, don't worry about which library to use.  */
  if (opts.nbytes == 0)
    return 0;
  
  // select correct function pointer
  void (*initialize)(const char *);
  unsigned long long (*rand64)(void);
  void (*finalize)(void);

  if (opts.input && opts.input[0] == '/')
  {
    initialize = software_rand64_init;
    rand64 = software_rand64;
    finalize = software_rand64_fini;
  }
  else if (opts.input && (strcmp(opts.input, "mrand48_r") == 0))
  {
    initialize = mrand48_rand64_init;
    rand64 = mrand48_rand64;
    finalize = mrand48_rand64_fini;
  }
  else if (!opts.input || strcmp(opts.input, "rdrand") == 0)
  {
    if (rdrand_supported())
    {
      initialize = hardware_rand64_init;
      rand64 = hardware_rand64;
      finalize = hardware_rand64_fini;
    }
    else
      return usage_error("rdrand is not supported on this machine.");
  }
  else
    return usage_error("INPUT must be rdrand, mrand48_r, or /FILENAME.");
  
  // initialize functions
  if (opts.input && opts.input[0] == '/')
    initialize(opts.input);
  else
    initialize(NULL);
  int wordsize = sizeof(unsigned long long);

  // stdio output
  if (!opts.output_method || strcmp(opts.output_method, "stdio") == 0)
  {
      do
  {
    unsigned long long x = rand64();
    int outbytes = opts.nbytes < wordsize ? opts.nbytes : wordsize;

    if (!write_stdio(x, outbytes))
      return usage_error("Error in writing bytes.");

    opts.nbytes -= outbytes;

  } while (0 < opts.nbytes);

  }

  // block write output
  else if (strcmp(opts.output_method, "write") == 0)
  {
    // allocate buffer
    char* buffer = malloc(opts.block_size * sizeof(char));
    if (buffer == NULL)
      return usage_error("Failed to allocate buffer.");

    // write blocks

    int total_bytes = opts.nbytes;
    int block_size = wordsize < opts.block_size ? wordsize: opts.block_size;
    
    while (total_bytes > 0) {
      unsigned long long x = rand64();
      int num_bytes_to_print = block_size;
      if (total_bytes < block_size)
	num_bytes_to_print = total_bytes;

      if (!write_block(buffer, x, num_bytes_to_print))
	  return usage_error("Error in writing block.");
      
      total_bytes -= num_bytes_to_print;

    }

    free(buffer);
  }

  if (fclose(stdout) != 0)
    return usage_error("Error in closing file.");

  finalize();
  
  return 0;
}
