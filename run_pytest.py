import os,sys
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='params of pytest marks self-defined')
    parser.add_argument('--mark',nargs='+',help='marks to run pytest')
    args = parser.parse_args()
    if len(args.mark) > 1:
        command = 'pytest -qvs ./test -m "{}"'.format(' or '.join(args.mark))
    elif len(args.mark) == 1:
        command = 'pytest -qvs ./test -m "{}"'.format(args.mark[0])
    elif not args.mark:
        command = 'pytest -qvs ./test'
    else:
        print('参数错误')
        sys.exit(-1)

    os.system(command)