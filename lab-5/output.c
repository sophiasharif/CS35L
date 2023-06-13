#include <stdbool.h>
#include <stdio.h>
#include <limits.h>
#include <string.h>
#include <unistd.h>
#include "output.h"

bool write_stdio(unsigned long long x, int nbytes)
{
  do
    {
      if (putchar (x) < 0)
	return false;
      x >>= CHAR_BIT;
      nbytes--;
    }
  while (0 < nbytes);

    fflush(stdout);  // ensure all data is written to stdout
  return true;

}

bool write_block(char* buffer, unsigned long long x,  int block_size)
{
 // Copy the data to the buffer
 memcpy(buffer, &x, block_size);

 // Write the data from the buffer to stdout
 int bytes_written = write(STDOUT_FILENO, buffer, block_size);

 if (bytes_written < block_size) {
     perror("write_block: write failed");
     return false;
 }
 return true;
}
