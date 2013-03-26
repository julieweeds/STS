__author__ = 'mmb28'

def prebyblo_filter(input_file, filtered_tokens):
    with open(filtered_tokens) as fh:
        filtered = set(token.strip() for token in fh)


    with open(input_file) as infile:
        with open('%s.filtered' % input_file, 'w') as outfile:
            for line in infile:
                if line.split('\t')[0] not in filtered:
                    outfile.write(line)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print 'Usage: filter.py input_file tokens_to_filter'
        sys.exit(1)

    input_file = sys.argv[1]
    filtered_tokens = sys.argv[2]
    prebyblo_filter(input_file, filtered_tokens)
