
#ifndef OPTIONS
#define OPTIONS

struct options {
  char* input;
  char* output_method;
  int block_size;
  int nbytes;
};

int usage_error(char *error_message);

int parse_options(int argc, char **argv, struct options* opts);

#endif
