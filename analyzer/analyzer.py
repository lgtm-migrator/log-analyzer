import argparse
import re
import json
from datetime import datetime

from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from cassandra.cluster import Cluster
from kafka import KafkaProducer

APACHE_ACCESS_LOG_PATTERN = r'^(\S+) (\S+) (\S+) \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+) (\S+)" (\d{3}) (\d+)'


def parse_log_line(line):
    match = re.search(APACHE_ACCESS_LOG_PATTERN, line)
    result = None
    if match:
        date = datetime.strptime(match.group(4), '%d/%b/%Y:%H:%M:%S %z')
        date = date.isoformat()
        result = [
            match.group(1),       # ip_address
            match.group(2),       # client_identd
            match.group(3),       # user_id
            date,                 # date_time
            match.group(5),       # method
            match.group(6),       # endpoint
            match.group(7),       # protocol
            int(match.group(8)),  # response_code
            int(match.group(9))   # content_size
        ]
    return result


def process(partition, kafka_producer):
    session = connect_to_cassandra()
    for row in partition:
        insert_into_db(row, session)
    kafka_producer.send('dashboard', partition)


def insert_into_db(row, session):
    query = """
        INSERT INTO logs (
        ip_address, client_identd, user_id,
        date_time, method, endpoint, protocol,
        response_code, content_size)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    session.execute(query, row)


def connect_to_cassandra():
    cluster = Cluster()
    session = cluster.connect('logs_keyspace')
    return session


def main(interval, topic):
    conf = SparkConf().setAppName("Log Analyzer")
    sc = SparkContext(conf=conf)
    ssc = StreamingContext(sc, interval)
    kafka_stream = KafkaUtils.createDirectStream(
        ssc, [topic], {"bootstrap.servers": 'localhost:9092'})
    kafka_producer = KafkaProducer(
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        bootstrap_servers=['localhost:9092'])
    kafka_producer = sc.broadcast(kafka_producer)
    parsed = kafka_stream.map(lambda v: parse_log_line(v[1]))
    parsed.pprint()
    parsed.foreachRDD(
        lambda rdd: rdd.foreachPartition(
            lambda p: process(p, kafka_producer.value)))
    ssc.start()
    ssc.awaitTermination()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('interval', type=int, help='In seconds')
    parser.add_argument('topic', type=str, help='Kafka topic')
    args = vars(parser.parse_args())
    main(**args)
