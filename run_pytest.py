#encoding=utf-8
import os,sys
import argparse
import pytest

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='params of pytest marks self-defined')
    parser.add_argument('--mark',nargs='+',help='marks to run pytest')
    args = parser.parse_args()
    print('marks:{}'.format(args.mark))
    if not args.mark:
        pytest.main(
            ['-q', '-m' './test', '--alluredir=/data/allure-results'])
    else:
        if len(args.mark) > 1:
            pytest.main(
                ['-q', '-m' './test', '--alluredir=/data/allure-results', '-m', "{}".format(' or '.join(args.mark))])
        elif len(args.mark) == 1:
            pytest.main(
                ['-q', '-m' './test', '--alluredir=/data/allure-results', '-m', "{}".format(args.mark[0])])
        else:
            print('参数错误')
            sys.exit(-1)
