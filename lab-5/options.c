#include <errno.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdbool.h>
#include "options.h"


int usage_error (char *error_message)
{
  fprintf(stderr, error_message);
  fprintf(stderr, "\n");
  fprintf(stderr, "Usage: ./randall NBYTES [-i INPUT] [-o OUTPUT]\n");
  return 1;
}

int parse_options(int argc, char **argv, struct options* opts)
{
    /* check the number of args is correct */
  if (!(argc == 2 || argc == 4 || argc == 6))
    return usage_error("Incorrect number of args.");

  /* Check for input and output options */
  int opt;
  char *input = NULL;
  char *output = NULL;

  while ((opt = getopt(argc, argv, "i:o:")) != -1)
  {
    switch (opt)
    {
    case 'i':
      if (input != NULL)
        return usage_error("Multiple -i options not allowed");
      input = optarg;
      break;
    case 'o':
      if (output != NULL)
        return usage_error("Multiple -o options not allowed");
      output = optarg;
      break;
    default:
      return usage_error("Error in processing parameters.");
    }
  }

  opts->input = input;

  // process output
  if (output) {
    if (strcmp(output, "stdio") == 0) {
        opts->output_method = "stdio";
        opts->block_size = 0;
      }
      else
      {
	bool valid = false;
	char *endptr;
	errno = 0;
        long block_size = strtol(output, &endptr, 10);
        if (errno)
	  return usage_error("Error in processing block size.");
	else
	  valid = !*endptr && block_size > 0;
	if (!valid)
	  return usage_error("NBYTES must be stdio or a non-negative integer.");
        opts->output_method = "write";
        opts->block_size = block_size;
      }
  }
  
  /* find positional argument */
  char *nbytes_ptr = NULL;
  if (optind < argc)
  {
    nbytes_ptr = argv[optind];
    optind++; // Move to the next argument
  }

  // check if there are extra arguments not handled
  if (optind < argc)
    return usage_error("Extra arguments were provided");

  // check that a positional arg is passed
  if (nbytes_ptr == NULL)
    return usage_error("Please specify a number of bytes.");

  // process nbytes
  long long nbytes;

  bool valid = false;
  char *endptr;
  errno = 0;
  nbytes = strtoll(nbytes_ptr, &endptr, 10);
  if (errno)
    return usage_error("Error in processing number of bytes.");
  else
    valid = !*endptr && 0 <= nbytes;

  if (!valid)
    return usage_error("NBYTES must be a non-negative integer.");

  opts->nbytes = nbytes;
  
  return 0;
}


