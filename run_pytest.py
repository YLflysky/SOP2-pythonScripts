#encoding=utf-8
import os,sys
import argparse
import pytest
import subprocess

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='params of pytest marks self-defined')
    parser.add_argument('--mark',help='marks to run pytest')
    parser.add_argument('--env',help='choose test environment',choices=['DEV','SIT','UAT'])
    parser.add_argument('--gate',help='decide whether to user gateway',choices=['true','false'])
    args = parser.parse_args()
    if not args.env:
        print('please choose test environment:{}'.format('DEV,SIT,UAT'))
        sys.exit(-1)
    else:
        os.environ['ENV'] = args.env

    if not args.gate:
        print('please choose whether to use gateway:{}'.format('true,false'))
        sys.exit(-1)
    else:
        os.environ['GATE'] = args.gate

    print('marks:{}'.format(args.mark))
    print(len(args.mark))
    if not args.mark or len(args.mark) == 0:
        cmd = 'pytest -q ./test --alluredir /data/allure-results'
    else:
        marks = args.mark.split(',')
        if len(marks) > 1:
            cmd = 'pytest -q ./test --alluredir /data/allure-results -m {}'.format(' or '.join(marks))
        elif len(marks) == 1:
            cmd = 'pytest -q ./test --alluredir /data/allure-results -m {}'.format(marks[0])
        else:
            print('参数错误')
            sys.exit(-1)
        print(cmd)
        cmd.encode('utf-8').decode('utf-8')
        os.system(cmd)
