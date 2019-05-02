spark-submit --master local[*] \
	     --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.2 \
	     analyzer/analyzer.py 5 log_topic
