#encoding=utf-8
import os,sys
import argparse
import pytest

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='params of pytest marks self-defined')
    parser.add_argument('--mark',help='marks to run pytest')
    args = parser.parse_args()

    print('marks:{}'.format(args.mark))
    if not args.mark:
        pytest.main(
            ['-q', '-m' './test', '--alluredir=/data/allure-results'])
    else:
        marks = args.mark.split(',')
        if len(marks) > 1:
            pytest.main(
                ['-q', '-m' './test', '--alluredir=/data/allure-results', '-m', "{}".format(' or '.join(marks))])
        elif len(marks) == 1:
            pytest.main(
                ['-q', '-m' './test', '--alluredir=/data/allure-results', '-m', "{}".format(marks[0])])
        else:
            print('参数错误')
            sys.exit(-1)
