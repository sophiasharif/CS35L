# Make x86-64 random byte generators.

# Copyright 2015, 2020, 2021 Paul Eggert

# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.  */

# Optimization level.  Change this -O2 to -Og or -O0 or whatever.
OPTIMIZE =

# The C compiler and its options.
CC = gcc
CFLAGS = $(OPTIMIZE) -g3 -Wall -Wextra -fanalyzer \
  -march=native -mtune=native -mrdrnd

# The archiver command, its options and filename extension.
TAR = tar
TARFLAGS = --gzip --transform 's,^,randall/,'
TAREXT = tgz

default: randall

randall: randall.c rand64-hw.c rand64-sw.c output.c options.c
	$(CC) $(CFLAGS) randall.c rand64-hw.c rand64-sw.c output.c options.c -o $@

 assignment: randall-assignment.$(TAREXT)
assignment-files = COPYING Makefile randall.c
randall-assignment.$(TAREXT): $(assignment-files)
	$(TAR) $(TARFLAGS) -cf $@ $(assignment-files)

submission-tarball: randall-submission.$(TAREXT)
submission-files = $(assignment-files) \
  notes.txt *.c *.h
randall-submission.$(TAREXT): $(submission-files)
	$(TAR) $(TARFLAGS) -cf $@ $(submission-files)

repository-tarball:
	$(TAR) -czf randall-git.tgz .git

.PHONY: default clean assignment submission-tarball repository-tarball

clean:
	rm -f *.o *.$(TAREXT) randall

define run_test # use ($call run_test,TEST_NUM,COMMAND,EXPECTED_OUTPUT) to run
    @echo -e "=== TEST $(1) ===\n./randall $(2)"
    @count=$$(./randall $(2) | wc -c); \
    echo "Outputted $$count bytes."; \
    if [ "$$count" -eq $(3) ]; then \
        echo -e "Passed!\n"; \
    else \
        echo -e "Failed.\n"; \
    fi
endef

check:
	$(call run_test,1,70,70) 
	$(call run_test,2,100 -o stdio,100)
	$(call run_test,3,12 -i rdrand,12)
	$(call run_test,4,99 -i mrand48_r,99)
	$(call run_test,5,12000 -i /dev/urandom,12000)
	$(call run_test,6,3712 -o 17,3712)
	$(call run_test,7,-o stdio 18 -i mrand48_r, 18)
	$(call run_test,8,-i rdrand -o 1 723, 723)
	$(call run_test,9,-i rdrand -o 1 0, 0)
	$(call run_test,10,-o 65 1802, 1802)
