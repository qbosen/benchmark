from client_bench import *

content = """
$ ab -c500 -n1000 http://192.168.6.30:8301/public/columns/33/contents
This is ApacheBench, Version 2.3 <$Revision: 1826891 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 192.168.6.30 (be patient)
Completed 100 requests
Completed 200 requests
Completed 300 requests
Completed 400 requests
Completed 500 requests
Completed 600 requests
Completed 700 requests
Completed 800 requests
Completed 900 requests
Completed 1000 requests
Finished 1000 requests


Server Software:        Jetty(9.3.11.v20160721)
Server Hostname:        192.168.6.30
Server Port:            8301

Document Path:          /public/columns/33/contents
Document Length:        12306 bytes

Concurrency Level:      500
Time taken for tests:   1.067 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      12441000 bytes
HTML transferred:       12306000 bytes
Requests per second:    937.55 [#/sec] (mean)
Time per request:       533.304 [ms] (mean)
Time per request:       1.067 [ms] (mean, across all concurrent requests)
Transfer rate:          11390.69 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    9   9.0      2      26
Processing:     6  340 191.1    329     811
Waiting:        6  340 191.2    328     811
Total:          8  349 192.8    335     818

Percentage of the requests served within a certain time (ms)
  50%    335
  66%    404
  75%    462
  80%    491
  90%    654
  95%    726
  98%    765
  99%    789
 100%    818 (longest request)
 """
sorted_patterns = [
    BenchPattern("uri", r'Document Path:\s+(.+)'),
    BenchPattern("concurrency", r'Concurrency Level:\s+(\d+)', v_func=int),
    BenchPattern("requests", r'Complete requests:\s+(\d+)', v_func=int),
    BenchPattern("qps", r'Requests per second:\s+([\d.]+)\s.*', v_func=float),
    BenchPattern("tpr", r'Time per request:\s+([\d.]+)\s.*', v_func=float),
    BenchPattern("t_90", r'\s*90%\s+(\d+)', v_func=int),
]


def test_result_parse():
    bench = BenchCollection(sorted_patterns)
    result = bench.bench_result(content.splitlines())
    print(result)


def test_ab_result():
    bench = BenchCollection(sorted_patterns)
    result = bench.bench("https://www.taobao.com/", c=2, n=10)
    print(result)


if __name__ == '__main__':
    test_result_parse()
    test_ab_result()
