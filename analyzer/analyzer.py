import argparse
import re

from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql import Row
from cassandra.cluster import Cluster

APACHE_ACCESS_LOG_PATTERN = r'^(\S+) (\S+) (\S+) \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+) (\S+)" (\d{3}) (\d+)'


def parse_log_line(line):
    match = re.search(APACHE_ACCESS_LOG_PATTERN, line)
    result = None
    if match:
        result = Row(
            ip_address=match.group(1),
            client_identd=match.group(2),
            user_id=match.group(3),
            date_time=match.group(4),
            method=match.group(5),
            endpoint=match.group(6),
            protocol=match.group(7),
            response_code=int(match.group(8)),
            content_size=int(match.group(9)))
    return result


def send_data(rdd):
    pass


def process(rdd, session):
    rdd.foreach(lambda row: insert_into_db(row, session))
    #df = rdd.toDF().coalesce(1)
    # TODO: send data to dashboard


def insert_into_db(row, session):
    row = row.asDict()
    columns = ', '.join(row.keys())
    values = ', '.join(map(str, row.values()))
    print(columns, values)
    query = """
        INSERT INTO logs (%s)'
        VALUES (%s)
        """ % (columns, values)
    print(query)
    #session.execute(query)


def connect_to_cassandra(cluster_ips):
    cluster = Cluster(cluster_ips)
    session = cluster.connect()
    return session


def main(interval, kafka_broker_list, topic, cassandra_server):
    sc = SparkContext("local[*]", "LogAnalyzer")
    ssc = StreamingContext(sc, interval)
    #kafka_stream = ssc.socketTextStream("localhost", 9999)
    kafka_stream = KafkaUtils.createDirectStream(
        ssc, [topic], {"metadata.broker.list": kafka_broker_list})
    parsed = kafka_stream.map(lambda v: parse_log_line(v[1]))
    parsed = kafka_stream.map(parse_log_line)
    parsed.foreachRDD(process)
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
