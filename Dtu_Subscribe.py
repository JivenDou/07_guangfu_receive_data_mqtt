import paho.mqtt.client as mqtt
import logging.config
import os
import json

from Crypto.Cipher import AES
from tools.AES_crypt import AESCrypt
from tools.logging_config import LOGGING_CONFIG
from tools.logging_config import subscribe_log as logger


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

# aes数据加密
aes_passwd = "123456781234567"
aes_cryptor = AESCrypt(aes_passwd, AES.MODE_ECB)  # ECB模式


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT Broker!")
    else:
        logger.error(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    """！！！处理数据消息函数！！！"""
    # print("主题:" + msg.topic + " 消息:" + new_msg)
    try:
        if msg:
            new_msg = bytes.hex(msg.payload)[16:]
            print(f"主题:{msg.topic} 消息:{new_msg}")
            # 按两位提取出modbus返回指令数据
            modbus_list = [new_msg[i:i+2] for i in range(0, len(new_msg), 2)]
            print(modbus_list)
    except Exception as e:
        logger.error(repr(e))


class MqttSubClient:
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
    s_client = MqttSubClient(broker='192.168.1.33')    # 创建订阅者对象
    s_client.connect_mqtt("sencott", "123456")    # 连接服务器
    s_client.on_subscribe("SCH/#")     # 订阅消息并等待接收消息

