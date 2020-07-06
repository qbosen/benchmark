import os
import re

"""
用于在客户端发起基准测试
统计测试结果，保存数据
"""


class BenchPattern:
    """
    用于提取输入数据中的关键量
    按行返回一个bench结果
    """

    @staticmethod
    def group_1(matcher):
        """
        默认认为每行只匹配一个group
        :param matcher: 正则匹配的记过
        :return: 第一个group
        """
        return matcher.group(1)

    def __init__(self, name, pattern, m_func=group_1.__func__, v_func=str):
        """
        初始化正则模式
        :param name:匹配的属性名称
        :param pattern:正则
        :param m_func: 匹配时，matcher的获值函数
        :param v_func: 匹配时，m_func的值装配函数
        """
        self.name = name
        self.pattern = re.compile(pattern)
        self.m_func = m_func
        self.v_func = v_func

    def match(self, text):
        """
        匹配输入数据
        :param text:数据
        :return: 匹配结果，再通过自定义的包装函数转换
        """
        m = self.pattern.match(text)
        return self.v_func(self.m_func(m)) if m else None


"""ab的匹配模式，按顺序组合，优化执行"""
sorted_patterns = [
    BenchPattern("uri", r'Document Path:\s+(.+)'),
    BenchPattern("concurrency", r'Concurrency Level:\s+(\d+)', v_func=int),
    BenchPattern("requests", r'Complete requests:\s+(\d+)', v_func=int),
    BenchPattern("qps", r'Requests per second:\s+([\d.]+)\s.*', v_func=float),
    BenchPattern("tpr", r'Time per request:\s+([\d.]+)\s.*', v_func=float),
    BenchPattern("t_90", r'\s*90%\s+(\d+)', v_func=int),
]


class BenchCollection:
    """
    一个模式匹配集合，用于匹配一次bench的记过
    """
    def __init__(self, patterns=sorted_patterns):
        """
        :param patterns: 该集合所使用的模式集合
        """
        self.patterns = patterns

    def bench(self, url, c=50, n=10000):
        lines = os.popen(f"ab -c{c} -n{n} {url}").readlines()
        return self.bench_result(lines)

    def bench_result(self, lines):
        """
        根据自身顺序pattern，解析结果
        :param lines: 需要解析的行
        :return: 匹配的结果字典
        """
        res = {}
        idx = 0
        size = len(self.patterns)
        if not size:
            return res
        for line in lines:
            pattern = self.patterns[idx]
            ans = pattern.match(line)
            if ans:
                res[pattern.name] = ans
                idx += 1
            if idx >= size:
                break

        return res
