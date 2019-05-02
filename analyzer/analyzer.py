import argparse
import re
from collections import namedtuple
from datetime import datetime

from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql import Row
from cassandra.cluster import Cluster


APACHE_ACCESS_LOG_PATTERN = r'^(\S+) (\S+) (\S+) \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+) (\S+)" (\d{3}) (\d+)'

"""
            ip_address=match.group(1),
            client_identd=match.group(2),
            user_id=match.group(3),
            date_time=match.group(4),
            method=match.group(5),
            endpoint=match.group(6),
            protocol=match.group(7),
            response_code=int(match.group(8)),
            content_size=int(match.group(9))]
"""

def parse_log_line(line):
    match = re.search(APACHE_ACCESS_LOG_PATTERN, line)
    result = None
    if match:
        date = datetime.strptime(match.group(4), '%d/%b/%Y:%H:%M:%S %z')
        date = date.isoformat()
        result = [
            match.group(1),
            match.group(2),
            match.group(3),
            date,
            match.group(5),
            match.group(6),
            match.group(7),
            int(match.group(8)),
            int(match.group(9))]
    return result


def send_data(rdd):
    pass


def process(partition):
    session = connect_to_cassandra(['localhost'])
    for row in partition:
        insert_into_db(row, session)
    # TODO: send data to dashboard


def insert_into_db(row, session):
    #row = row.asDict()
    query = """
	INSERT INTO logs (ip_address, client_identd, user_id, date_time, method, endpoint, protocol, response_code, content_size)
	VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    print(query)
    session.execute(query, row)


def connect_to_cassandra(cluster_ips):
    cluster = Cluster(cluster_ips)
    session = cluster.connect('logs_keyspace')
    return session


def main(interval, kafka_broker_list, topic, cassandra_server):
    sc = SparkContext("local[*]", "LogAnalyzer")
    ssc = StreamingContext(sc, interval)
    kafka_stream = KafkaUtils.createDirectStream(
        ssc, [topic], {"bootstrap.servers": 'localhost:9092'})
    parsed = kafka_stream.map(lambda v: parse_log_line(v[1]))
    parsed.pprint()
    parsed.foreachRDD(lambda rdd: rdd.foreachPartition(process))
    ssc.start()
    ssc.awaitTermination()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('interval', type=int, help='In seconds')
    parser.add_argument('topic', type=str, help='Kafka topic')
    parser.add_argument(
        'cassandra_server', type=str, help='Cassandra server ip')
    parser.add_argument(
        'kafka_broker_list', type=str, help='Kafka broker list', nargs='+')
    args = vars(parser.parse_args())
    main(**args)
