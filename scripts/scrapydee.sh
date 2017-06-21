#!/bin/bash

FUNC=$1
SRVR=$2

EGG="steam_scraper-1.0-py3.6.egg"

if [ -z "$FUNC" ]
then
    FUNC='status'
fi
echo "Executing $FUNC()..."

if [ -z "$SRVR" ]
then
    SRVR='all'
fi
echo "On server(s): $SRVR."

copy_urls() {
    scp ../output/review_urls_$1.txt scrapy-runner-$1:/home/ubuntu/run/
}

copy_egg() {
    scp ../dist/$EGG scrapy-runner-$1:/home/ubuntu/run
}

add_egg() {
    ssh -f scrapy-runner-$1 'cd /home/ubuntu/run && curl http://localhost:6800/addversion.json -F project=steam -F egg=@'$EGG
}

list_versions() {
    ssh -f scrapy-runner-$1 'curl http://localhost:6800/listversions.json?project=steam'
}

status() {
    ssh -f scrapy-runner-$1 "curl http://localhost:6800/daemonstatus.json"
}

start() {
    ssh -f scrapy-runner-$1 "cd /home/ubuntu/run && source env/bin/activate && nohup scrapyd -l scrapyd.log &"
}

stop() {
    ssh -f scrapy-runner-$1 "pkill scrapyd"
}

job_cancel() {
    ssh scrapy-runner-$1 'curl http://localhost:6800/cancel.json -d project=steam -d job=part_'$1
}

job_start() {
    ssh scrapy-runner-$1 'curl http://localhost:6800/schedule.json -d project=steam -d spider=reviews -d url_file="/home/ubuntu/run/review_urls_'$1'.txt" -d jobid=part_'$1' -d setting=FEED_URI="s3://'$STEAM_S3_BUCKET'/%(name)s/part_'$1'/%(time)s.jl" -d setting=AWS_ACCESS_KEY_ID='$AWS_ACCESS_KEY_ID' -d setting=AWS_SECRET_ACCESS_KEY='$AWS_SECRET_ACCESS_KEY' -d setting=LOG_LEVEL=INFO'
}

all() {
    for i in {1..3}
    do
	local n=$(printf %02d $i)
	${1} $n
    done
}

if [ "$SRVR" == "all" ]
then
    all $FUNC
else
    if ! [[ "$SRVR" =~ ^[0-9]+$ ]]
    then
        echo "Server parameter must be an integer or 'all'."
        exit 1
    fi

    if ! ((SRVR >= 1 && SRVR <= 3))
    then
        echo "Server must be between 1 and 3."
        exit 1
    fi

    n=$(printf %02d $SRVR)
    ${FUNC} $n
fi

exit 0
