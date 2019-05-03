#!/bin/bash
bin/kafka-topics.sh --zookeeper logger.descifrandolinux.com:2181 --create --replication-factor 1 --partitions 1 --topic log_topic
