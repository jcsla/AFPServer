#! /bin/sh

#----------------------------------------------------------------
# Startup script for the server of Solr
#----------------------------------------------------------------

# configuration variables
prog="solrservice"

# start the server
start(){
	printf 'Starting the server of Solr\n'
	cd /home/afpapi/echoprint-server/solr/solr/
	java -Dsolr.solr.home=/home/afpapi/echoprint-server/solr/solr/solr/ -Djava.awt.headless=true -jar /home/afpapi/echoprint-server/solr/solr/start.jar &
}

# stop the server
stop(){
	printf 'Stopping the server of Solr\n'
	# ps -f | grep Dsolr | grep -v grep | awk '{printf("%s ", $2);}' | xargs kill -9
	ps aux | grep -ie Dsolr | awk '{print $2}' | xargs kill -9 
	# pkill -9 Dsolr
}

# dispatch the command
case "$1" in
start)
	start
	;;
stop)
	stop
	;;
restart)
	stop
	sleep 2
	start
	;;
*)
	printf 'Usage: %s {start|stop|restart}\n' "$prog"
	exit 1
	;;
esac

# exit
exit "$retval"

# END OF FILE
