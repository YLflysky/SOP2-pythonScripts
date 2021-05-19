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

    def write_value(self,key,value):
        '''
        往redis中写入普通类型的值
        '''

        self.conn.set(key,value)
        print('写入键值对成功:{}->{}'.format(key,value))

    def write_set_value(self,key,value):
        '''
        往redis中写入set类型的值
        '''

        self.conn.sadd(key,value)
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
        res = set()
        for val in value:
            res.add(val.decode())
        print('获取到的值为:{}'.format(res))
        return res

    def get_hash_value(self,key):
        '''
        获取redis中hash类型的值
        '''
        value = self.conn.hgetall(key)
        res = {}
        for k,v in value.items():
            res[k.decode()] = v.decode()
        print('获取到的值为:{}'.format(res))
        return res

    def set_hash_value(self,big_key,small_key,value:dict):
        '''
        注入hash值
        '''
        value = self.conn.hset(big_key,small_key,value)
        print('写入{}键值对成功:{}-->{}'.format(big_key,small_key,value))

    def get_list_value(self,key):
        '''
        获取redis中list类型的值
        '''
        # length = self.conn.llen(key)
        value = self.conn.lrange(key,0,-1)
        res = []
        for v in value:
            res.append(v.decode())
        print('获取到的值为:{}'.format(res))
        return res

    def set_list_value(self,big_key,small_key,value:dict):
        '''
        注入hash值
        '''
        value = self.conn.hset(big_key,small_key,value)
        print('写入{}键值对成功:{}-->{}'.format(big_key,small_key,value))

    def del_key(self,*key):
        self.conn.delete(*key)
        print("删除数据成功:{}".format(key))

