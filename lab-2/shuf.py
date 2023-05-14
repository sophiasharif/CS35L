'''
Homework 2
Sophia Sharif

shuf:
    --echo (-e),
    --input-range (-i),
    --head-count (-n),
    --repeat (-r),
    --help.
'''
import argparse
import random, sys, string
from argparse import ArgumentParser


class RandLine:
    def __init__(self, filename):
        self.lines = []
        if type(filename) == str:
            with open(filename) as file:
                self.lines = file.readlines()
        if type(filename) == list:
            self.lines = filename
        self.lines = [line.rstrip() for line in self.lines]
        random.shuffle(self.lines)

    def choose_line(self):
        return random.choice(self.lines)


def process_input_range(parser, args):

    if not args.input_range:
        return None

    # verify i was not set multiple times
    if len(args.input_range) > 1:
        parser.error("multiple -i options specified")

    if args.file:
        parser.error(f"extra operand {args.file}")

    input_range = args.input_range[0][0].split('-')

    if len(input_range) != 2 or not input_range[0].isdigit() or not input_range[1].isdigit():
        parser.error(f"invalid input range: ‘{args.input_range[0][0]}’")

    lo, hi = int(input_range[0]), int(input_range[1])

    if lo < 0 or hi < 0 or hi < lo:
        parser.error(f"invalid input range: ‘{args.input_range[0][0]}’")

    return lo, hi+1


def process_head_count(parser, args):
    if args.head_count is None:
        return None
    count = min(args.head_count)[0]
    if not count.isdigit():
        parser.error(f"invalid line count: '{count}'")
    count = int(count)

    if count < 0:
        parser.error(f" invalid line count: {count}")
    return count


def handle_echo(named_args, other_args, max_output):

    if max_output is None:
        # don't cap output if we don't care about head count
        max_output = float('inf')

    output = other_args + [named_args.file]
    random.shuffle(output)
    count = 0

    for word in output:
        if max_output <= 0:
            break
        sys.stdout.write(word + '\n')
        max_output -= 1
        count += 1

    return count    # return number of lines outputted


def handle_input_range(lo, hi, max_output):

    if max_output is None:
        # don't cap output if we don't care about head count
        max_output = float('inf')

    output = list(range(lo, hi))
    random.shuffle(output)
    count = 0

    for num in output:
        if max_output <= 0:
            break
        sys.stdout.write(str(num) + '\n')
        max_output -= 1
        count += 1

    return count


def handle_file(parser, file, max_output):

    try:
        generator = None
        if file is None or file == '-':
            generator = RandLine(sys.stdin.readlines())
        else:
            generator = RandLine(file)

        # if output is not capped, we wish to output each line in the file exactly once
        if max_output is None:
            for line in generator.lines:
                sys.stdout.write(line + '\n')
            return

        # if a max output is specified, just choose lines at random.
        for index in range(max_output):
            sys.stdout.write(generator.choose_line() + '\n')

    except IOError:
        parser.error(f"{file}: No such file or directory")


def main():
    # set up parser
    usg_msg = """ 
    shuf [OPTION]... [FILE]
      or:  shuf -e [OPTION]... [ARG]...
      or:  shuf -i LO-HI [OPTION]...
    Write a random permutation of the input lines to standard output.

    With no FILE, or when FILE is -, read standard input.
      """
    parser = ArgumentParser(prog="shuf", usage=usg_msg)
    parser.add_argument(dest='file', nargs='?', help=argparse.SUPPRESS)
    parser.add_argument('-e', '--echo', action='store_true', help="treat each ARG as an input line")
    parser.add_argument('-i', '--input-range', action='append', nargs=1,
                        help="treat each number LO through HI as an input line.")
    parser.add_argument('-n', '--head-count',  action='append', nargs=1, help="output at most COUNT lines.")
    parser.add_argument('-r', '--repeat', action="store_true", help="output lines can be repeated.")

    # set up args
    named_args, other_args = parser.parse_known_args()
    i_range = process_input_range(parser, named_args)
    head_count = process_head_count(parser, named_args)

    if named_args.echo and i_range:
        parser.error("cannot combine -e and -i options")

    # -r option:
    if named_args.repeat:
        count = float('inf')
        if head_count is not None:
            count = head_count

        while count > 0:
            if named_args.echo:
                count -= handle_echo(named_args, other_args, 1)
            elif i_range:
                count -= handle_input_range(i_range[0], i_range[1], 1)
            else:
                handle_file(parser, named_args.file, count)
                break

    # not -r option:
    else:
        if named_args.echo:
            handle_echo(named_args, other_args, head_count)
        elif i_range:
            handle_input_range(i_range[0], i_range[1], head_count)
        else:
            handle_file(parser, named_args.file, head_count)


if __name__ == '__main__':
    main()
