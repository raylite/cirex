#!/bin/sh
source cirexenv/bin/activate

while true; do
	flask db upgrade
	if [[ "$?" == "0" ]]; then
	break
	fi
	echo Upgrade command failed, retrying in 5 secs ...
	sleep 5
done
exec gunicorn -b :5000 \
--workers 2 \
--timeout 300000 \
--graceful-timeout 300000 \
--keep-alive 300000 \
--access-logfile - \
--error-logfile - \
cirex_launch:app
