import os
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='params of pytest marks self-defined')
    parser.add_argument('--mark',nargs='+',help='marks to run pytest')
    args = parser.parse_args()
    if args.mark:
        command = 'pytest -qvs ./test -m "{}"'.format(' or '.join(args.mark))
    else:
        command = 'pytest -qvs ./test'
    os.system(command)