"""
lk_logger v2.6.4

更新日志:
    1.3
        调整了 print_important_msg() 中 output_path 参数的位置
        调整了 print_important_msg() 的缩进
        print_important_msg() 的 show_details 参数默认改为 True
        增加了一个 total_count 内置对象
    1.4
        优化了计时器逻辑, 使用 lk.over(), 取代以前的 lk.start_timer() 和 lk.over_timer()
        优化了注释文档
        将 high_level_info_collector 中的 'enabled' 键删除
        扩增了 print_important_msg() 的捕获范围
        更新了 LKLogger 的注释文档, 统一了之前的格式, 以及增加了打印重要信息时的推荐写法
        cycle_point() 即将抛弃, 建议改用 divider_line()
        divider_line() 增加 mirror 参数, 以及更新了进阶操作的相关说明
        增加一个 counter 和 counter_denominator 变量, 用来给特定打印行计数
        删除 lk.start_timer() 和 lk.over_timer()
        divider_line() 增加 count_up 参数
        divider_line() 的 "remark" 参数改为 "msg" 并调换到第一位
    2.0
        使用 inspect 模块的 stack() 方法重构 prt()
        大幅减少动态模板代码量
        精简初始化 logger 操作
    2.1
        增加 log_container 列表对象和 dump_log() 方法
        dump_log() 增加 use_shortname 参数
        将 dump_log() 的 use_shortname 改为 custom_filename, 并支持自定义命名前缀
        恢复 self.high_level_info_collector_activated 对象
        整合 dump_log() 的参数, 使用智能判定
        更新注释文档
    2.2
        升级 high_level_info_collector
        增加一个 live template ("lke")
        high_level_info_collector 内部根据 tag 进行排序整理
        将 print_important_msg() 的统计步骤放在了打印后
        增加一个 record_launch_func(), 用于记录当前运行程序的启动参数
        dump_log() 增加一个格式, 可以选择打印出启动文件名 + 启动函数名
        将时间戳单独为一个函数 generate_time_stamp()
        generate_time_stamp() 增加 style 参数
        删除 self.high_level_info_collector_activated 对象
        修复 prt() 中 count_up 的格式错误
        当 high_level_info_counter.values() 全部为0时, 则不打印
        将 hierarchy 改为内部对象, 不再在函数中暴露
    2.3
        init_counter() 逻辑调整优化
        over() 当平均速度为 "0.0s/个" 时, 转换成毫秒显示
        在 main() 中打印出 start_time
        增加 hierarchy_detain 成员, 以修复打印行号错误
        取消 hierarchy 和 hierarchy_detain 成员, 将 hierarchy 改为 prt() 的参数之一
        调整 divider_line() 的 count_up 参数位置
        优化 generate_time_stamp() 方法, 使更加智能
        调换 generate_time_stamp() 的两个参数 (ctime 和 style) 的位置
        将 generate_time_stamp() 的 style 的默认样式从 'y-m-d_hms' 修改为 'y-m-d h:m:s'
        counter_limit 重命名为 counter_denominator
        优化 update_info_collector() 的正则表达式
        prt() 中增加多变量打印时的格式美化 (分号转制表符)
        创建 prt_table() 方法
    2.4
        微调 prt() 中使用 self.update_info_collector(msg) 的位置
    2.5
        使用 sys.argv 替代 main() 函数, 省去每次初始化 logger 的操作
        优化 init_path_manager() 方法
        完善 LKLogger 的注释
        record_launch_func() 改名为 prt_fun_args(), 并简化功能
        取消 find_context(), 将其整合到 prt_fun_args()
        取消 dump_log() 的 add_funname 参数
        增加 prt_auto 及相关方法
        find_caller() 增加 line 变量
        优化相对路径的计算方法
        当总耗时低于0.01s时, 切换到毫秒显示
        简化打印格式 (由 'File "main.py", line 12 ...' 变为 'main.py:12 ...')
        更新注释文档, 使支持最新方法格式
        增强 auto_create_msg() 兼容性
        prt_auto() 重命名为 smart_prt()
        优化 divider_line() 的样式生成方法
    2.6
        将 auto_create_msg() 重命名为 smart_msg()
        优化 smart_msg() 方案, 适配更多场景
        修复 smart_msg() 对 count_up 参数的识别
        优化 divider_line() 容错度
        优化 smart_msg() 输出样式的细节
        smart_msg() 增加 len(raw_data) == 1 的快速判断
        over() 在打印时, 增加一条分割线
        优化 smart_msg() 容错度
        smart_msg() 增加对 format 的支持
        优化 smart_msg() 输出样式的细节 (多参数之间由 '\t' 分隔改为 ';\t' 分隔)

"""

import re
from inspect import stack
from os.path import isdir
from sys import argv
from time import localtime, strftime, time


def find_caller(hierarchy=2):
    """
    假设有这么一条调用链:
        函数 a() 调用了函数 b(), 函数 b() 调用了函数 c(), 函数 c() 调用了本函数 find_caller(), 则存在以下层级:
            hierarchy=0 --> stack()[0] --> 该层级是 find_caller() 层
            hierarchy=1 --> stack()[1] --> 该层级是函数 c() 层
            hierarchy=2 --> stack()[2] --> 该层级是函数 b() 层
            hierarchy=3 --> stack()[3] --> 该层级是函数 a() 层
        在每一层中, 都可以获得该层函数的 "所属文件名", "函数名", "所处的行号" 这三个信息. 以 a() 为例:
            stack()[3][0] --> 表示函数 a() 的所在 frame
            stack()[3][1] --> 表示函数 a() 的所在文件名
            stack()[3][2] --> 表示函数 a() 的所在行号
            stack()[3][3] --> 表示函数 a() 的所在函数名

    由于 LKLogger 只存在以下两种调用链:
        1. 外部函数调用了 LKLogger.prt(), LKLogger.prt() 再调用本函数 find_caller() --> 则外部函数的层级永远是 hierarchy=2
        2. 外部函数调用了 LKLogger.divider_line(), LKLogger.divider_line() 再调用 LKLogger.prt(), LKLogger.prt() 再调用本
        函数 find_caller() --> 则外部函数位于的层级是 hierarchy=3 (我们可以通过在 divider_line() 中给 hierarchy 改为3就行了)

    参考:
        https://blog.csdn.net/qiqiyingse/article/details/70766993
        http://www.cnblogs.com/qq78292959/p/3289658.html
        https://www.cnblogs.com/yyds/p/6901864.html

    :param hierarchy: int. 取2或3
        hierarchy=0 --> self.find_caller()
        hierarchy=1 --> self.prt() who is calling self.find_caller()
        hierarchy=2 --> somefunc() who is calling self.prt()
        hierarchy=3 --> somefunc() who is calling self.divider_line()

    :return: path, lineno, func
        path: str. 完整路径, 用 '/' 连接
        lineno: int. 行号
        func: str. 外部调用函数
        line: str. 行内容
    """
    # print(stack())  # test
    context = stack()[hierarchy]
    
    path, lineno, func, line = context[1:5]
    # path, lineno, func = context[1:4]
    # line = stack()[2][4]
    '''
        注意事项: 如果您的外部函数是这样的:
            def main():
                lk.prt(
                    'hello',
                    a,
                    b
                )
        则 line 只能显示 "        b\n".
    '''
    
    if '\\' in path:
        path = path.replace('\\', '/')
    
    if func != '<module>':
        func += '()'
    
    # line = ['        lk.prt('hello', a + b)']
    line = line[0].strip()  # --> 'lk.prt('hello', a + b)'
    
    return path, lineno, func, line


class LKLogger:
    """
    基本操作:
        导入lk_logger:
            from common_utils.lk_logger import lk
        在控制台打印一条信息:
            lk.prt('hello')
            # 输出效果: test.py:12  >>  foo()  >>  hello
        在控制台打印变量信息:
            a, b = 1, 2
            lk.prt('a + b = {}'.format(a + b))
            # 输出效果: test.py:16  >>  foo()  >>  a + b = 3
        统计运行时长:
            lk.over()
            '''输出效果
                test.py:23  >>  <module>  >>  开始运行: 2018-11-14 12:35:15
                test.py:23  >>  <module>  >>  结束运行: 2018-11-14 12:36:30
                test.py:23  >>  <module>  >>  总耗时: 1.25min
            '''
        统计运行时长以及计算出平均速度:
            lk.total_count = 300
            lk.over()
            '''输出效果
                test.py:23  >>  <module>  >>  开始运行: 2018-11-14 12:35:15
                test.py:23  >>  <module>  >>  结束运行: 2018-11-14 12:36:30
                test.py:23  >>  <module>  >>  总耗时: 1.25min
                test.py:23  >>  <module>  >>  共处理300个. 平均速度0.25s/个
            '''
        保存log到本地:
            lk.dump_log()
            # 默认会保存到 "../log/" 目录下, 并以启动文件的文件名加时间戳来命名此log

    --------------------------------------------------

    进阶操作:
        打印重要的信息:
            lk.prt('[D]this is a debug')
            lk.prt('[I]this is an info')
            lk.prt('[W]this is a warning')
            lk.prt('[E]this is an error')
            '''输出效果
            lk_logger会在结束计时后, 收集运行中所有出现过的重要信息, 并在日志末尾按照类别排序后统一打印出来:
                test.py:1   >>  foo()  >>  ------------------------ here the collected msg which were important
                test.py:11  >>  foo()  >>  [D]this is a debug
                test.py:12  >>  foo()  >>  [I]this is an info
                test.py:13  >>  foo()  >>  [W]this is a warning
                test.py:14  >>  foo()  >>  [E]this is an error
                                [D] count = 1
                                [I] count = 1
                                [W] count = 1
                                [E] count = 1
                                [C] count = 0
            '''
        打印一条分割线:
            lk.divider_line('a new start')
            # 输出效果:
            # test.py:1  >>  foo()  >>  ----------------------------------------------------------- a new start
        打印一条分割线, 并自定义分割线的风格:
            lk.divider_line('a new start', style='◆', length=10, mirror=True)
            # 输出效果:
            # test.py:1  >>  foo()  >>  ◆◆◆◆◆◆◆◆◆◆ a new start ◆◆◆◆◆◆◆◆◆◆
        对特定的打印行显示序号:
            示例1: 直接计数
                fruit = ['apple', 'orange', 'banana']
                for i in fruit:
                    lk.prt('i = {}'.format(i), count_up=True)  # 进行打印计数
                    '''输出效果
                        test.py:11  >>  foo()  >>  [1] i = apple
                        test.py:11  >>  foo()  >>  [2] i = orange
                        test.py:11  >>  foo()  >>  [3] i = banana
                    '''

            示例2: 先告诉logger一共有多少行, 再计数
                fruit = ['apple', 'orange', 'banana']
                lk.init_counter(len(fruit))  # 告诉logger一共有多少行待打印
                for i in fruit:
                    lk.prt('i = {}'.format(i), count_up=True)  # 进行打印计数
                    '''输出效果
                        test.py:11  >>  foo()  >>  [1/3] i = apple
                        test.py:11  >>  foo()  >>  [2/3] i = orange
                        test.py:11  >>  foo()  >>  [3/3] i = banana
                    '''
        将log保存到本地, 并自定义它的位置:
            ps: 建议在脚本结束的地方使用

            示例1: 指定输出目录
                lk.dump_log('../log/org_ability_extractor/')

            示例2: 指定输出文件名
                lk.dump_log('../log/extractor.txt')
                '''
                    logger会识别到 'extractor' 这个文件名, 并添加一个时间戳, 最终输出为:
                    '../log/extractor_2018-12-01_162811.txt'
                '''

            示例3: 告诉logger使用短写 (以 "org_ability_extractor.py" 为启动文件讲解)
                # 示例2-1
                lk.dump_log('shortname')  # 'shortname' 是logger内置的关键词
                # 最终输出为: '../log/oae_2018-12-01_162811.txt'

                # 示例2-2
                lk.dump_log('../log/org_ability_extractor/shortname')
                # 最终输出为: '../log/org_ability_extractor/oae_2018-12-01_162811.txt'

    --------------------------------------------------

    特点:
        1. 结合 live templates 使用
        2. 打印出来的所有信息都可以点击定位到源代码所在行

    --------------------------------------------------

    动态模板配置:
        缩写: lki
        描述: lk init
        输出: from common_utils.lk_logger import lk

        缩写: lk
        描述: lk print
        输出: lk.prt('$msg$')

        缩写: lka
        描述: lk smart print
        输出: lk.prt_auto($var$)

        缩写: lkf
        描述: lk print with format
        输出: lk.prt('$msg$ = {}'.format($msg$))

        缩写: lke
        描述: lk print error
        输出: lk.prt('[$level$$code$] $msg$'.format($var$))
        变量: $code$ --> time("mmss")

        缩写: lkd
        描述: lk divider line
        输出: lk.divider_line('$msg$ = {}'.format($msg$))

    --------------------------------------------------

    LKLogger的实现逻辑:
        背景知识:
            1. 利用 sys.argv 获得启动文件的绝对路径
                python 的 sys.argv 参数是一个列表对象, 里面是当前启动的脚本的绝对路径. 例如:
                    # abc.py
                    from sys import argv

                    if __name__ == '__main__':
                        print(argv)
                        # 输出: ['d:/my_project/app/abc.py']

                因此利用 argv 可以获得启动脚本的绝对路径.
            2. 在控制台打印出可以跳转到代码所在位置的信息
                观察一个报错事件:
                    # abc.py
                    print(3 / 0)
                我们在控制台可以看到:
                    Traceback (most recent call last):
                      File "D:/my_project/app/abc.py", line 12, in <module>
                        main(123)
                      File "D:/my_project/app/abc.py", line 7, in main
                        print(3 / 0)
                    ZeroDivisionError: division by zero
                其中这两个路径被 pycharm 识别到了, 变为蓝色的链接, 可以点击跳转到源代码位置, 也就是报错的行.
                pycharm 是怎么识别到这个链接的呢?

                再举一个例子:
                    print('http://www.baidu.com')
                同样在控制台能看到 url 被标记为蓝色链接.

                说明 pycharm 可以根据文本规则识别为特定的蓝色链接.

                所以我们模仿报错内容的写法:
                    print('File "D:/my_project/app/abc.py", line 7, hello')
                发现控制台确实识别成功了, 而且点击就能跳转到第七行.
                通过进一步试验, 以下打印都能被识别:
                    # 1. 使用相对路径
                    print('File "abc.py", line 7')
                    # 2. 跳转到指定的行
                    print('File "abc.py", line 123')
                    # 3. 甚至跳转到别的文件
                    print('File "../utils/def.py", line 12')

                通过这两个发现, 我们可以做到:
                    1. 让打印出来的每行信息都能跳转到打印的源代码所在位置
                    2. 使用相对路径的写法, 可以让打印的内容更简洁
            3. 利用stack模块追踪源码路径, 行号, 函数名等信息
                详见 find_caller() 方法
        LKLogger 的主体实现:
            假设有:
                ~/my_project
                    /aaa/a.py
                    /bbb/b.py
                在 a 中引入 b. 并以 a 为启动脚本.
            1. 首先 LKLogger 利用 sys.argv 获得 a 的绝对路径
            2. LKLogger 将 a 的绝对路径作为主路径, 并加入到 "路径字典" 中:
                self.path_manager = {a 的绝对路径: a 的相对路径}
            3. 然后将 b 的相对路径计算出来, 也加入到 "路径字典" 中:
                self.path_manager = {a 的绝对路径: a 的相对路径, b 的绝对路径: b 的相对路径}
                # b 的绝对路径怎么获得? --> 详见 find_caller() 方法
                # 已知 a 的绝对路径和 b 的绝对路径, 怎么求 b 的相对路径? --> 详见 calculate_relative_path(a, b) 方法
            4. 当 a 调用 LKLogger 打印时:
                1. LKLogger 利用 find_caller() 获得 a 调用打印的代码所在的绝对路径, 行号, 以及函数名信息
                2. LKLogger 现在有了这三个信息, 可以利用 pycharm 能识别的格式来 "组装" 一条消息:
                    print('File "{a 的相对路径}", line {a 调用时的源码所在行号} >> {a 的调用打印行所属的函数名} >> {打印的内容}')
                3. 至此, 就实现了打印功能.
            5. 在 b 中调用 LKLogger 也是同样的道理. 注意 a 和 b 引用的是同一个 logger 实例, 因此 logger 是可以区分 a 和 b 的路径的.

    --------------------------------------------------

    注意事项:
        目前只支持单线程的打印, 多线程无法区分线程名.
    """
    
    # 启用 logger
    enabled = True  # 控制 Logger 是否启用, 当启用时, 才会打印信息. 该功能用于控制在多线程中只允许某个线程打印
    
    # 打印选项
    show_func = True  # 是否打印所属函数名
    """
        show_func = True --> 打印效果: test.py:18  >>  main()  >>  hello.
        show_func = False --> 打印效果: test.py:18  >>  hello.
    """
    log_container = []  # 日志记录容器, 用于在结束运行时, 将容器里面的记录保存到指定的 log 目录下
    
    # 路径管理器, 负责存储运行时收集到的所有模块的相对启动模块的相对路径
    # 其存储的键值对形式为: {绝对路径: 相对路径}
    # 特别的, 对于启动文件(也就是 if __name__ == "__main__" 的文件), 将它的绝对路径赋值给 launch_path
    path_manager = {}
    launch_path = ''
    
    # 计时参数, 用于计算总耗时, 以及平均速度
    start_time = 0
    end_time = 0
    total_count = 0  # 总计数
    counter = 0  # 计数器
    counter_denominator = 0  # 计数器的分母 (可选)
    """
    关于总计数与计数器的区别:
        总计数用于计算处理的总量, 计数器适合对某个循环体进行计数.
        例如有两个循环体:
            a = ((11, 12, 13), (21, 22, 23, 24), (31, 32))
            for i in a:
                lk.init_counter(len(i))  # 设置一个分母
                for j in i:
                    lk.prt('j = {}'.format(j), count_up=True)  # count_up 表示启用计数
                    lk.total_count += 1
            lk.prt('total_count = {}'.format(lk.total_count))
        计数效果如下:
            [1/3] j = 11
            [2/3] j = 12
            [3/3] j = 13
            [1/4] j = 21
            [2/4] j = 22
            [3/4] j = 23
            ...
            total_count = 9
    """
    
    # 重要信息收集器
    high_level_info_counter = {
        'D': 0, 'I': 0, 'W': 0, 'E': 0, 'C': 0,
    }  # 日志级别: debug < info < warning < error < critical
    high_level_info_collector = {'D': [], 'I': [], 'W': [], 'E': [], 'C': [], }
    
    # ----------------------------------------------------------------
    
    def __init__(self):
        self.start_time = time()  # 开始计时
        self.init_path_manager()
        print('start time = {}'.format(generate_time_stamp('y-m-d h:m:s', self.start_time)))
    
    def enable_logger(self, switch):
        assert isinstance(switch, bool)
        self.enabled = switch
    
    def init_counter(self, total_count=0):
        """
        初始化计数器
        给即将要计数的循环体, 取其长度作为分母, 设置给 self.counter_denominator.

        推荐:
            假如有两个相互嵌套的循环体:
                for i in range(10):
                    for j in range(100):
                        ...
            推荐给小循环体初始化计数器.

        :param total_count:
        :return:
        """
        if total_count == 0:
            self.counter = 0
        else:
            if isinstance(total_count, list):
                total_count = len(total_count)
            elif isinstance(total_count, float):
                total_count = int(total_count)
            
            assert isinstance(total_count, int) and total_count > 0
            
            self.counter = 0
            self.counter_denominator = total_count
    
    # ----------------------------------------------------------------
    
    def init_path_manager(self):
        self.launch_path = argv[0]
        # print(argv[0])  # test
        if '\\' in self.launch_path:
            self.launch_path = self.launch_path.replace('\\', '/')
        self.path_manager[self.launch_path] = re.sub(r'.+/', '', self.launch_path)
        # --> {'d:/my_project/app/folder1/test.py': 'test.py'}
    
    def update_path_manager(self, new_path):
        """
        该函数用于将导入的模块所在的路径的绝对路径加入到路径管理器中

        :param new_path: str. e.g. 'd:/my_project/app/folder1/test1.py'
        :return:
        """
        # assert self.launch_path  # todo test
        relative_path = calculate_relative_path(self.launch_path, new_path)
        self.path_manager[new_path] = relative_path
    
    # ----------------------------------------------------------------
    pattern2 = re.compile(r'\[[^]]+\]')
    
    def prt(self, msg, count_up=False, hierarchy=2):
        """

        :param msg: str. e.g. '[D1240] subpage found'
        :param count_up:
        :param hierarchy
        :return:
        """
        if self.enabled:
            filepath, lineno, func, line = find_caller(hierarchy)
            # 假设外部函数 foo() 调用了 prt(), prt() 在这里调用了 find_caller(2), 则此处返回的是 foo() 的上下文信息
            
            if filepath not in self.path_manager.keys():
                self.update_path_manager(filepath)
            
            # -------------------------------- calculate counter
            if count_up:
                self.counter += 1
                if self.counter_denominator > 0:
                    count_tag = '[{}/{}]'.format(self.counter, self.counter_denominator)  # --> '[1/100]'
                else:
                    count_tag = '[{}]'.format(self.counter)  # --> '[1]'
                
                if msg[0] == '[':
                    # msg = '[D1240] subpage found'
                    tag = self.pattern2.findall(msg)[0]  # --> '[D1204]'
                    msg = msg.replace(tag, tag + count_tag)
                    # '[D1240] subpage found' --> '[D1240][1/100] subpage found'
                else:
                    msg = count_tag + ' ' + msg  # 'subpage found' --> '[1/100] subpage found'
            
            # -------------------------------- whether to show function name in msg
            if self.show_func:
                msg = '{}:{}\t>>\t{}\t>>\t{}'.format(
                    self.path_manager[filepath],  # got the relative path name
                    lineno, func, msg
                )  # --> 'test.py:16  >>  foo()  >>  out print some msg'
            else:
                msg = '{}:{}\t>>\t{}'.format(
                    self.path_manager[filepath],
                    lineno, msg
                )  # --> 'test.py:16  >>  out print some msg'
            
            # -------------------------------- prettify outlook of msg
            if '>>\t[' in msg and '; ' in msg:
                msg = msg.replace('. ', '.\t', 1).replace('; ', '\t')
                """
                示例:
                    msg = 'test.py:6  >>  foo()  >>  [I1004] out print some msg. index = 2; data = "a"'
                    --> 'test.py:6  >>  foo()  >>  [I1004] out print some msg.\tindex = 2\tdata = "a"'
                为什么要这样做?
                    为了兼顾书写美观和打印美观.
                    比如我们在写代码的时候, 用分号比直接用\t要好看 (后者显得太紧凑).
                    而在打印的时候, 转换为\t一来可以让纵列对齐美观, 另一方面在复制到excel中时, 能自动分开格子.
                """
            self.update_info_collector(msg)
            
            # -------------------------------- printing and recording this msg
            print(msg)
            self.log_container.append(msg)
    
    def smart_prt(self, *var, count_up=False, hierarchy=3):
        """

        极端案例演示:
            G = 'G'
            H = 1
            I = [1]
            J = [2]
            lk.smart_prt("A", "(B), ", "C\'D, {}".format("E\\\"F"), G, -2 * int(H), tuple(zip(I, J)), count_up=True)
            '''
            在示例中, 存在以下情况:
                单引号和双引号
                大中小括号
                元素内存在逗号
                字符串内存在转义字符, 比如 "A\"B"
                字符串内存在非转义字符, 比如 "A'B"
            '''
            '''
            抽取效果:
                ['"A"', '"(B), "', '"C●D, {}".format("E\\\\●F")', 'G', '-2 * int(H)', 'tuple(zip(I, J))']
            输出效果
                test2.py:8  >>  <module>  >>  
                    [1] A; (B), ; C'D, E\"F; G = G; -2 * int(H) = -2; tuple(zip(I, J)) = ((1, 2),)
            '''

        注意:
            使用本方法请务必确保书写时不要有换行:
                # 错误
                lk.prt_auto(
                    a,
                    b
                )
            该情况会导致变量打印风格丢失, 也就是说不会输出 "a = 1; b = 2", 而会输出 "1; 2"

        :param hierarchy:
        :param count_up:
        :param var:
        :return:
        """
        filepath, lineno, func, line = find_caller()
        msg = self.smart_msg(line, var)
        self.prt(msg, count_up=count_up, hierarchy=hierarchy)
    
    smart_msg_pattern = re.compile(r'(?<=smart_prt\().+(?=\))')
    
    def smart_msg(self, line, raw_data):
        """
        
        参考:
            成对符号的捕获和处理

        注: 目前本函数的局限性:
            1. 对于 `'A\'B'` 这种情况无法处理 (因为在 python 中, 该字符串是被当作 `'A'B'`, 因此无解), 只能处理 `'A\\\'B'` 这种情况

        :param line:
        :param raw_data:
        :param count_up:
        :return:
        """
        raw_data = tuple(map(str, raw_data))
        
        if '.smart_prt(' not in line:
            '''
            注: 暂不支持智能处理以下形式:
                lk.smart_prt(
                    a, b
                )
                lk.smart_prt(a,
                             b)
            针对这类情况, 本函数将只返回 raw_date 的处理结果
            '''
            return ';\t'.join(raw_data)
        
        line = self.smart_msg_pattern.findall(line)[0]
        
        # ---------------------------------------------------------------- 简单判断1: raw_date 长度为1的情况
        quote_symbol = ("'", '"')
        
        if len(raw_data) == 1:
            '''
            e.g.
                lk.smart_prt(zip(a, b, c))
            '''
            if line[0] in quote_symbol:
                return raw_data[0]
            else:
                return '{} = {}'.format(line, raw_data[0])
        
        # ---------------------------------------------------------------- 
        raw_msg = [x.strip() for x in line.split(',') if 'count_up=' not in x and 'hierarchy=' not in x]
        
        if len(raw_msg) == len(raw_data):
            # -------------------------------- 简单判断2: line 简单切分的数量与 raw_data 一致
            pass
        
        else:
            # -------------------------------- 复杂判断
            line = ', '.join(raw_msg) + ','
            
            if '\\\'' in line:
                line = line.replace('\\\'', '●')
            if '\\"' in line:
                line = line.replace('\\"', '●')
                
            if "'.format(" in line:
                line = line.replace("'.format(", "',.format(")
            if '".format(' in line:
                line = line.replace('".format(', '",.format(')
                
            pairing_symbol = ("'", '"', '(', ')', '[', ']', '{', '}')
            bracket_match = {')': '(', ']': '[', '}': '{', '(': ')', '[': ']', '{': '}'}
            quote_counter = {"'": 0, '"': 0, '(': 0, ')': 0, '[': 0, ']': 0, '{': 0, '}': 0}
            
            holder = ''
            last_symbol = ''
            pause = ','
            
            raw_msg = []
            
            for index, char in enumerate(line):
                if index == 0:
                    last_char = ''
                else:
                    last_char = line[index - 1]
                
                if char in pairing_symbol:
                    if char in bracket_match.keys():
                        if quote_counter['"'] % 2 == 0 and quote_counter["'"] % 2 == 0:
                            quote_counter[char] += 1
                            last_symbol = char
                    else:
                        another_quote_type = '"' if char == "'" else "'"
                        if quote_counter[another_quote_type] % 2 == 0:
                            quote_counter[char] += 1
                            last_symbol = char
                
                elif char == pause:
                    if not last_symbol:
                        # update
                        if holder[0:8] == '.format(':
                            raw_msg[-1] += holder.strip()
                        else:
                            raw_msg.append(holder.strip())
                        holder, last_symbol = '', ''
                        continue
                    
                    if last_char == last_symbol:
                        if quote_counter['"'] % 2 == 0 and quote_counter["'"] % 2 == 0:
                            if (last_symbol in ('"', "'")) or (
                                    last_symbol in bracket_match.keys() and
                                    quote_counter[last_symbol] == quote_counter[bracket_match[last_symbol]]):
                                # update
                                if holder[0:8] == '.format(':
                                    raw_msg[-1] += holder.strip()
                                else:
                                    raw_msg.append(holder.strip())
                                holder, last_symbol = '', ''
                                continue
                
                holder += char
        
        # ---------------------------------------------------------------- 整理输出
        # print(raw_msg)  # test
        msg = []
        
        # assert len(raw_msg) == len(raw_data)
        for i in range(len(raw_msg)):
            m, n = raw_msg[i], raw_data[i]
            if m[0] in quote_symbol or m[-1] in quote_symbol:
                msg.append(n)
            else:
                msg.append('{} = {}'.format(m, n))
        
        return ';\t'.join(msg)
    
    def prt_table(self, header: list, *mlist, style='\t'):
        """

        :param header:
        :param mlist: an abbr of "multi lists"
        :param style
        :return:
        """
        hierarchy = 3
        
        table_contents = ['\n', '\t' + style.join(header)]
        
        mrows = zip(*mlist)
        
        for r in mrows:
            r = map(str, r)
            table_contents.append('\t' + style.join(r))
        
        table_contents.append('\n')
        
        self.prt(table_contents, hierarchy=hierarchy)
    
    def prt_fun_args(self):
        """
        如果你想要打印所在函数的参数, 则使用本方法.

        :return:
        """
        # print(stack(2))  # debug
        fun_args = stack()[2][4][0].strip()
        '''
            stack()[2] --> FrameInfo(
                frame=<
                    frame at 0x0000020AC410E9F8,
                    file 'D:/likianta/lk_workspace/com_qwings_data/scopus_scholar_spider_3/lab/test.py',
                    line 35,
                    code <module>
                >,
                filename='D:/likianta/lk_workspace/com_qwings_data/scopus_scholar_spider_3/lab/test.py',
                lineno=35,
                function='<module>',
                code_context=['    main()\n'],
                index=0
            )
            stack()[2][4] --> ['    main()\n']
            stack()[2][4][0] --> '    main()\n'
            stack()[2][4][0].strip() --> 'main()'
        '''
        hierarchy = 3
        self.prt('print function args: {}'.format(fun_args), hierarchy=hierarchy)
    
    def divider_line(self, msg='', count_up=False, style='-', length=64, mirror=False, hierarchy=3):
        """
        打印一条分割线, 适合在主循环的每次循环开始处使用, 使 console 中的信息更便于阅读

        样式示例:
            lk.divider_line()
            # 输出效果:
            # test.py:1  >>  foo()  >>  --------------------------------------------------

            lk.divider_line(msg='a new start')
            # 输出效果:
            # test.py:1  >>  foo()  >>  -------------------------------------------------- a new start

            lk.divider_line(msg='a new start', style='◆', length=10, mirror=True)
            # 输出效果:
            # test.py:1  >>  foo()  >>  ◆◆◆◆◆◆◆◆◆◆ a new start ◆◆◆◆◆◆◆◆◆◆

        :param msg: str. 在分割线的末尾备注一些信息
        :param style: str. 自定义分割线的样式
        :param length: int. 自定义分割线的长短
        :param mirror: bool.
            False: ---------- a new start
            True: ---------- a new start ----------
        :param count_up: boolean.
        :param hierarchy: int
        :return:
        """
        s = style
        divider = s * length
        
        if mirror:
            msg = '{} {} {}'.format(divider, msg, divider)
        else:
            msg = '{} {}'.format(divider, msg)
        
        self.prt(msg, count_up, hierarchy=hierarchy)
    
    # ----------------------------------------------------------------
    pattern1 = re.compile(r'(?<=>>\t)\[[DIWEC][-0-9a-zA-Z]*\]')
    """
        该匹配式用于捕捉重要信息
        支持捕捉的信息如下:
            [D], [DEBUG], [Debug], [Debug1016], [D0577], ...
            [I], [INFO], [Info], [Info1016], [I0577], ...
            [W], [WARNING], [Warning], [Warning1016], [W0577], ...
            [E], [ERROR], [Error], [Error1016], [E0577], ...
            [C], [CRITICAL], [Critical], [Critical1016], [C0577], ...
    """
    
    def update_info_collector(self, msg):
        """
        将高级别的醒目信息存入该对象
        为了便于重要信息的收集和良好打印, 请参考 print_important_msg() 的注释文档的推荐写法

        :param msg: str. 'test.py:16  >>  foo()  >>  [D0533] this is an important msg'
        :return:
        """
        if self.high_level_info_collector:
            tag = self.pattern1.findall(msg)
            # msg = 'test.py:16  >>  foo()  >>  [D0533] this is an important msg' --> tag = ['[D0533]']
            
            if tag:
                tag = tag[0]
                # ['[D0533]'] --> '[D0533]'
                keyname = tag[1:2]
                # '[D0533]' --> 'D'
                tag = tag[1:-1]
                # '[D0533]' --> 'D0533'
                
                self.high_level_info_counter[keyname] += 1
                # {'D': 0, 'I': 0, 'W': 0, 'E': 0, 'C': 0} --> {'D': 1, 'I': 0, 'W': 0, 'E': 0, 'C': 0}
                
                self.high_level_info_collector[keyname].append((msg, tag))
    
    def print_important_msg(self, show_details=True, output='console'):
        """
        为了打印出可读性更好的信息, 推荐使用以下写法(1):
            # 推荐
            lk.prt('[E]an error happened at url = {}'.format(url))
            # 不推荐
            lk.prt('[E]an error happened.')


        为了打印出可读性更好的信息, 推荐使用以下写法(2):
            # 推荐
            lk.prt('[E]network error'
                   '\tlicno = {}'
                   '\tbaseinfo_id = {}'
                   '\turl[t] = {}'.format(licno, baseinfo_id, url[t]))
            # 不推荐
            lk.prt('[E]network error')
            lk.prt('[E]licno = {}'.format(licno))
            lk.prt('[E]baseinfo_id = {}'.format(baseinfo_id))
            lk.prt('[E]url[t] = {}'.format(url[t]))

        为什么?
            通常我们会选择把重要的信息保存到日志文件或者粘贴到一个表格里面
            前者的表格显示效果为:
                | test.py:15 | >> | [E]network error | licno = '0577' | baseinfo_id = ... | url[t] = ... |
            这样我们可以很清楚地看到这三个变量是紧密相关的,在筛选排序时也不会失联

            而后者的表格显示效果为:
                | test.py:15 | >> | [E]network error              |
                | test.py:16 | >> | [E]licno = '0577'             |
                | test.py:17 | >> | [E]baseinfo_id = '234234'     |
                | test.py:18 | >> | [E]url[t] = 'http://h123.com' |
            假如日志中有很多条此类资讯, 那么就有可能在筛选, 排序等操作后, 这三个变量不能确定联系了

        :param show_details:
        :param output:
        :return:
        """
        hierarchy = 4
        
        if self.enabled and self.high_level_info_collector:
            # debug < info < warning < error < critical
            
            if any(self.high_level_info_counter.values()):
                if output == 'console':
                    self.divider_line('here the collected msg which were important', hierarchy=hierarchy)
                    
                    if show_details:  # 显示详情
                        for key_code in self.high_level_info_collector.keys():
                            # key_code = 'D', 'I', 'W', 'E', 'C'
                            
                            self.high_level_info_collector[key_code].sort(key=lambda r: r[1])
                            '''
                                对msg_list进行排序,比如:
                                    before:
                                        {
                                            'D': [
                                                ('test.py:16  >>  foo()  >>  [D0533] 111', 'D0533'),
                                                ('test.py:16  >>  foo()  >>  [D0621] 333', 'D0621'),
                                                ('test.py:16  >>  foo()  >>  [D0533] 222', 'D0210'),
                                            ],
                                            'I': [...], ...
                                        }
                                    after:
                                        {
                                            'D': [
                                                ('test.py:16  >>  foo()  >>  [D0533] 222', 'D0210'),
                                                ('test.py:16  >>  foo()  >>  [D0533] 111', 'D0533'),
                                                ('test.py:16  >>  foo()  >>  [D0621] 333', 'D0621'),
                                            ],
                                            'I': [...], ...
                                        }

                                参考:
                                    "~/demo/python_function_demo/python_list_skills.py" - sort_by_arg()
                            '''
                            
                            for msg in self.high_level_info_collector[key_code]:
                                # --> msg = ('test.py:16  >>  foo()  >>  [D0533] 222', 'D0210')
                                print(msg[0])
                                self.log_container.append(msg[0])
                    
                    # 统计
                    for key_code in self.high_level_info_counter.keys():
                        msg = '\t\t\t\t[{}] count = {}'.format(
                            key_code,
                            self.high_level_info_counter[key_code]
                        )
                        print(msg)  # --> '          [INFO] count = 4'
                        self.log_container.append(msg)
                
                else:
                    pass  # todo
            
            # shut down logger
            self.high_level_info_collector = None
    
    # ----------------------------------------------------------------
    
    def over(self, total_count=0):
        hierarchy = 3
        
        if self.enabled and self.start_time > 0:
            lk.divider_line(hierarchy=hierarchy + 1)
            
            self.end_time = time()
            
            self.prt("开始运行: {}".format(generate_time_stamp('y-m-d h:m:s', self.start_time)),
                     hierarchy=hierarchy)
            self.prt("结束运行: {}".format(generate_time_stamp('y-m-d h:m:s', self.end_time)),
                     hierarchy=hierarchy)
            
            # ---------------------------------------------------------------- calculate duration
            total_elapsed_time_sec = self.end_time - self.start_time
            if total_elapsed_time_sec < 0.01:
                duration = '{}ms'.format(round(total_elapsed_time_sec * 1000, 2))
            elif total_elapsed_time_sec < 60:
                duration = '{}s'.format(round(total_elapsed_time_sec, 2))
            else:
                duration = '{}min'.format(round(total_elapsed_time_sec / 60, 2))
            self.prt('总耗时 {}'.format(duration), hierarchy=hierarchy)
            
            # ---------------------------------------------------------------- calculate speed
            if total_count == 0 and self.total_count > 0:
                total_count = self.total_count
            if total_count > 0:
                speed = total_elapsed_time_sec / total_count  # 3.3333333 --> 3.33
                if speed < 0.01:
                    speed *= 1000
                    unit = 'ms'
                else:
                    unit = 's'
                self.prt('共处理{}个. 平均速度{}{}/个'.format(total_count, round(speed, 2), unit), hierarchy=hierarchy)
        else:
            self.prt('cannot count down lk logger clocker, '
                     'maybe logger is shut down or start time missed', hierarchy=hierarchy)
    
    def dump_log(self, output_path='../log/'):
        """
        dump_log()的参数output_path支持传入文件或目录

        支持的关键词(保留字):
            shortname: 用于识别并转换成缩略语(取启动文件的文件名的每个单词的首字母组成)

        转化规则如下(设启动文件为"my_launcher.py"):
            传入参数: '' --> 生成文件: '../log/test_launcher_2018-12-01_170110.txt'
            传入参数: '../log/abc.txt' --> 生成文件: '../log/abc_2018-12-01_170219.txt'
            传入参数: '../log/launcher/' --> 生成文件: '../log/launcher/test_launcher_2018-12-01_170141.txt'
            传入参数: 'shortname' --> 生成文件: '../log/tl_2018-12-01_170256.txt'
            传入参数: '../log/launcher/shortname.txt' --> 生成文件: '../log/launcher/tl_2018-11-23_225948.txt'
            传入参数: '../log/launcher/shortname' --> 生成文件: '../log/launcher/tl_2018-11-23_225948.txt'

        注:
            暂不支持文件夹使用shortname, 例如以下情况是不能处理的:
                ../log/shortname/abc.txt

        :param output_path:
        :return:
        """
        hierarchy = 3
        
        if self.enabled:
            use_shortname = False
            
            if output_path == '':
                output_path = '.'
            elif output_path == 'shortname':
                output_path = '../log/'
                use_shortname = True
            elif 'shortname' in output_path:
                output_path = output_path.replace('shortname', '').replace('.txt', '')
                use_shortname = True
            
            # ----------------------------------------------------------------
            ctime = time()
            time_stamp = generate_time_stamp('y-m-d_hms', ctime)
            
            # ----------------------------------------------------------------
            if output_path[-1] == '/' or isdir(output_path):
                # 说明output_path是一个目录, 比如说是'../log/1126/'
                
                filename = self.path_manager[self.launch_path][:-3]
                if use_shortname:
                    filename = ''.join([x[0] for x in filename.split('_')])
                    # 'excel_extractor' --> ['excel', 'extractor'] --> ['e', 'e'] --> 'ee'
                
                filename = '/{}_{}.txt'.format(filename, time_stamp)
                
                output_path = output_path.strip('/') + filename
                # --> 'tests/test_2018-11-26_154645.txt'
            else:
                '''
                    '../log/org_ability_extractor/oae_r1.txt'
                    '../log/org_ability_extractor/shortname.txt'
                    '../log/org_ability_extractor/shortname'
                '''
                if use_shortname:
                    filename = self.path_manager[self.launch_path][:-3]
                    filename = ''.join([x[0] for x in filename.split('_')])
                    filename = '/{}_{}.txt'.format(filename, time_stamp)
                    
                    output_path = output_path.strip('/') + filename
                else:
                    output_path = output_path.replace('.txt', '_{}.txt'.format(time_stamp))
            
            with open(output_path, encoding='utf-8', mode='w') as f:
                f.write(
                    'script launched at {}'
                    '\nscript filename is {}'
                    '\nlog dumped at {}'
                    '\n\n--------------------------------------------------\n\n'.format(
                        self.launch_path,
                        self.path_manager[self.launch_path],
                        generate_time_stamp('y-m-d h:m:s', ctime)
                    )
                )
                f.write('\n'.join(self.log_container))
            
            self.prt('log dumped at "{}"'.format(output_path), hierarchy=hierarchy)
            # self.enabled = False


def calculate_relative_path(a, b):
    """
    计算相对路径:
        已知两个绝对路径 a 和 b, 求 b 相对于 a 的相对路径.

    思路:
        在这个问题中, 我们的前提条件是 a 和 b 来自同一盘符.
        我们把 a 和 b 看作两条河流, 由于它们来自于同一个 "源头" (比如说是 D 盘), 所以这两条河流存在以下三种情况:
            1. a 和 b 属于同一条河的上下游:
                a = 'D:/M/N/a.py'
                b = 'D:/M/N/O/b.py'
            2. b 和 a 属于同一条河的上下游:
                a = 'D:/M/N/O/a.py'
                b = 'D:/M/N/b.py'
            3. a 和 b 是两条支流:
                a = 'D:/M/N/O/a.py'
                b = 'D:/M/N/P/b.py'
        这三种情况有一个共性, 就是 a 和 b 必有一个河流的交汇点.
        因此求 b 相对于 a 的路径, 可以分成两方面看待, 首先求 a 回溯到交汇点, 然后从交汇点顺流而下到 b.
        交汇点的求法很简单, 就是 a 和 b 最后一个相等的路径点;
        回溯的求法也很简单, 我们拿源头到 a 的长度减去源头到交汇点的长度, 再乘以 "../", 即可得到回溯路径;
        而顺流查找, 只取交汇点以后的路径就可以了.

    示例:
        a = 'd:/my_project/app/folder1/test1.py'
        b = 'd:/my_project/app/folder2/test2.py'
        期望输出: out = '../folder2/test2.py'

    参考:
        1. Python：获取当前py的文件名 - CSDN博客 https://blog.csdn.net/qcyfred/article/details/78434281

    """
    
    a, b = a.split('/'), b.split('/')
    
    intersection = 0
    
    for index in range(min(len(a), len(b))):
        m, n = a[index], b[index]
        if m != n:
            intersection = index
            break
    
    def backward():
        return (len(a) - intersection - 1) * '../'
    
    def forward():
        return '/'.join(b[intersection:])
    
    out = backward() + forward()
    return out


def generate_time_stamp(style='y-m-d h:m:s', ctime=0.0):
    """
    特点:
        支持自动判断参数中的'm'是月份还是分钟

    注:
        目前仅支持补零数字, 比如6月2日, 会生成为 "06-02"
        如果传入参数不符合常识, 则参数中的 'm' 可能会翻译错误

    :param ctime:
    :param style: str.
        'y-m-d_hms' --> '2018-12-27_151345'
    :return: str. e.g. '2018-12-27_151345'
    """
    if not ctime:
        ctime = time()
    ctime = localtime(ctime)
    
    # time_dict = {
    #     'year'  : '%Y',
    #     'month' : '%m',
    #     'day'   : '%d',
    #     'hour'  : '%H',
    #     'minute': '%M',
    #     'second': '%S'
    # }
    
    m = len(style.split('m'))
    if m == 3:
        style = style.replace('m', '%M').replace('%M', '%m', 1)
        """
        注:
            %m 表示月份
            %M 表示分钟

        注意:
            不要使用:
                style = style.replace('m', '%m', 1).replace('m', '%M', 1)
            分析它的处理过程, 会发现:
                y-m-d h:m:s --> y-%m-d h:m:s --> y-%%M-d h:m:s
            目前修正后的方法:
                style = style.replace('m', '%M').replace('%M', '%m', 1)
            的处理过程为:
                y-m-d h:m:s --> y-%M-d h:%M:s --> y-%m-d h:%M:s
            这才是正确的
        """
    elif m == 2:
        if 'y' in style or 'd' in style:
            style = style.replace('m', '%m', 1)
        else:
            style = style.replace('m', '%M', 1)
    else:
        pass
    style = style.replace('y', '%Y').replace('d', '%d').replace('h', '%H').replace('s', '%S')
    # 'y-m-d h:m:s' --> '%Y-%m-%d %H:%M:%S'
    
    time_stamp = strftime(style, ctime)
    
    return time_stamp


# ---------------------------------------------------------------- instantiate

lk = LKLogger()


def a_test():
    a = 'D:/likianta/lk_workspace/com_qwings_data/人才库/sstir_nlp_system/temp/tmp.py'
    b = 'D:/likianta/lk_workspace/com_qwings_data/人才库/sstir_nlp_system/utils/time_utils.py'
    c = calculate_relative_path(a, b)
    print(c)


if __name__ == '__main__':
    a_test()