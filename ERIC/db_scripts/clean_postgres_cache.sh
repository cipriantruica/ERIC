#!/bin/bash
#run as root
service postgresql stop
echo 3 > /proc/sys/vm/drop_caches
service postgresql start

