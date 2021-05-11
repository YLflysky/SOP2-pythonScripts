import redis
import os
from box.db import RedisConfig

class RedisUtils():
    def __init__(self,host='SOP2'):
        self.env = os.getenv('ENV')
        host_map = eval('RedisConfig.{}_{}.value'.format(host, self.env))
        ip = host_map['host']
        port = host_map['port']
        password = host_map['password']
        pool = redis.ConnectionPool(host=ip, port=port, password=password)
        self.conn = redis.Redis(connection_pool=pool)

    def write_key_redis(self ,key ,value):
        '''
        往redis中写入键值对
        '''

        self.conn.set(key,value)
        print('写入键值对成功:{}->{}'.format(key,value))

    def get_key_redis(self,key):
        '''
        获取redis中str类型的值
        '''
        value = self.conn.get(key)
        print('获取到的值为:{}'.format(value))
        return value

    def get_set_value(self,key):
        '''
        获取redis中set类型的值
        '''
        value = self.conn.smembers(key)
        print('获取到的值为:{}'.format(value))
        return value

    def get_hash_value(self,key):
        '''
        获取redis中hash类型的值
        '''
        value = self.conn.hvals(key)
        print('获取到的值为:{}'.format(value))
        return value