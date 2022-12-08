import paho.mqtt.client as mqtt
import logging.config
import os
import json
import configparser

from Crypto.Cipher import AES
from tools.AES_crypt import AESCrypt
from tools.logging_config import LOGGING_CONFIG
from tools.logging_config import subscribe_log as logger
from tools.hard_Disk_storage import HardDiskStorage

# logging config
logging.config.dictConfig(LOGGING_CONFIG)
handlers = LOGGING_CONFIG['handlers']
for handler in handlers:
    item = handlers[handler]
    if 'filename' in item:
        filename = item['filename']
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)


# --------------------------
def on_connect(client, userdata, flags, rc):
    """mqtt连接时"""
    if rc == 0:
        logger.info("Connected to MQTT Broker!")
    else:
        logger.error(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    """！！！处理数据消息函数！！！"""
    # print("主题:" + msg.topic + " 消息:" + new_msg)
    try:
        if msg:
            # print(f"主题:{msg.topic} 消息:{msg.payload}")
            # 解码获取数据
            aes_msg = msg.payload.decode()
            de_msg = aes_cryptor.aesdecrypt(aes_msg)
            dic_msg = json.loads(json.loads(de_msg))
            print('------------------------------')
            print(f"{type(dic_msg)},{dic_msg}")
            # 处理并插入数据
            parse_save_data(dic_msg['data'])
    except Exception as e:
        logger.error(repr(e))


def parse_save_data(datas):
    # 遍历所有设备表的数据
    for device_data in datas:
        # device_data={'DQ_DI': '0', 'STS_DI': '0', 'code': 'GI410_A', 'ts': 1670392422495, 'times': '2022-12-07 13:47:07',
        # 'c2': '12.34', 'c3': '12.34', 'c4': '12.34', 'c5': '12.34', 'c6': '12.34','c7': '12.34', 'c8': '12.34', 'c9': '12.34'}
        logger.info(device_data)
        # 若设备质量无效，就不解析此设备的数据
        if device_data['DQ_DI'] == '0' and device_data['STS_DI'] == '0':
            table_name = 'table_' + device_data['code']
            # 取出字典中数据的键和值
            li = ['DQ_DI', 'STS_DI', 'code', 'ts', 'times']
            keys = [key for key in device_data.keys() if key not in li]
            values = [device_data[key] for key in device_data.keys() if key not in li]
            # 向表内插入新数据
            sql = f"INSERT INTO `{table_name}`(times,{','.join(keys)}) " \
                  f"VALUES('{device_data['times']}',{','.join(values)});"
            db.execute_sql(sql)


class MqttSubClient:
    """mqtt订阅者类"""

    def __init__(self, broker, client_id='', port=1883, timeout=60):
        self.__client = None
        self.__broker = broker
        self.__port = port
        self.__timeout = timeout
        self.__client_id = client_id

    def connect_mqtt(self, username, password=None):
        try:
            self.__client = mqtt.Client(self.__client_id)
            self.__client.on_connect = on_connect
            self.__client.username_pw_set(username, password)
            self.__client.connect(host=self.__broker, port=self.__port, keepalive=self.__timeout)
            logger.info("connect success!")
        except Exception as e:
            logger.error(f"[MqttSubClient][connect_mqtt]connect error:{repr(e)}")

    def on_subscribe(self, topic):
        """订阅消息"""
        try:
            self.__client.subscribe(topic)
            self.__client.on_message = on_message
            self.__client.loop_forever()  # 循环，当有消息立刻调用on_message进行消息打印
        except Exception as e:
            logger.error(f"[MqttSubClient][subscribe]error:{repr(e)}")


if __name__ == "__main__":
    # 创建读取配置文件对象
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8")
    # 获取通用配置项
    section = "General"  # 读取的部section标签
    mysql_host = config.get(section, 'mysqlHost')
    mysql_username = config.get(section, 'mysqlUsername')
    mysql_password = config.get(section, 'mysqlPassword')
    mysql_port = config.getint(section, 'mysqlPort')
    # 获取特有配置项
    section = 'iotServerMQTT'  # 读取的部section标签
    mysql_database = config.get(section, 'mysqlDatabase')
    mqtt_HOST = config.get(section, 'mqttHost')
    mqtt_PORT = config.getint(section, 'mqttPort')
    mqtt_client_id = config.get(section, 'mqttClientId')
    mqtt_username = config.get(section, 'mqttUsername')
    mqtt_password = config.get(section, 'mqttPassword')
    mqtt_topic = config.get(section, 'mqttTopic')
    # 连接数据库
    db = HardDiskStorage(user=mysql_username, passwd=mysql_password, db=mysql_database, ip=mysql_host, port=mysql_port)
    # 获取Aes加密配置项
    section = 'Aes'  # 读取的部section标签
    aes_key = config.get(section, 'aesKey')
    aes_cryptor = AESCrypt(aes_key, AES.MODE_ECB)  # ECB模式
    # mqtt订阅客户端
    s_client = MqttSubClient(broker=mqtt_HOST, client_id=mqtt_client_id, port=mqtt_PORT)  # 创建订阅者对象
    s_client.connect_mqtt(username=mqtt_username, password=mqtt_password)  # 连接服务器
    s_client.on_subscribe(mqtt_topic)  # 订阅消息并等待接收消息
