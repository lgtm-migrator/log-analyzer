import argparse

from pyspark import SparkContext
from pyspark.streaming import StreamingContext

sc = None
ssc = None


def main(num_threads, interval):
    global sc, ssc
    # Create a local StreamingContext with two working thread and batch interval of 1 second
    sc = SparkContext("local[2]", "LogAnalyzer")
    ssc = StreamingContext(sc, interval)
    lines = ssc.socketTextStream("localhost", 9999)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'dataset', type=str, help='Predefined datasets or a csv file')
    args = vars(parser.parse_args())
    main(**args)
