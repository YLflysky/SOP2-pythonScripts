#encoding=utf-8
import os,sys
import argparse
import pytest

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='params of pytest marks self-defined')
    parser.add_argument('--mark',nargs='+',help='marks to run pytest')
    parser.add_argument('--env',type=str,help='choose env to run test case',choices=['DEV','SIT','UAT'])
    args = parser.parse_args()
    if not args.env:
        print('请指定测试环境:{}'.format('DEV,SIT,UAT'))
        sys.exit(-1)
    else:
        os.environ['ENV'] = args.env
        os.environ['GATE'] = 'false'
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
