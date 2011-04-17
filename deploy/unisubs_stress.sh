#!/bin/bash

deployment="staging"

page_create="http://$deployment.universalsubtitles.org/videos/create/"
page_demo="http://$deployment.universalsubtitles.org/demo/"
page_main="http://$deployment.universalsubtitles.org/"
page_videos="http://$deployment.universalsubtitles.org/videos/"

if [ "$deployment" == "www" ]; then
   page_team="http://www.universalsubtitles.org/en/teams/dare2bdigital/"
elif [ "$deployment" == "staging" ]; then
   page_team="http://staging.universalsubtitles.org/ru/teams/volunteers/"
fi

#----------------------------------
# Function reports error message and exits
error() {
   local msg="$1"

   echo "ERROR: $msg"
   echo "Usage: `basename $0` <num> team | main | demo | videos | create | randomize"
   exit 1
}

#----------------------------------
# Check command line arguments
if [ -z "$1" ]; then
   error "You must specify a number of requests to send"
fi
num_requests="$1"

if [ -z "$2" ]; then
   error "You must specify a test page"
fi

if [ "$2" == "team" ]; then
   testpage="$page_team"

elif [ "$2" == "main" ]; then
   testpage="$page_main"

elif [ "$2" == "demo" ]; then
   testpage="$page_demo"

elif [ "$2" == "videos" ]; then
   testpage="$page_videos"

elif [ "$2" == "create" ]; then
   testpage="$page_create"

elif [ "$2" == "randomize" ]; then
   testpage=""
   pagelist[0]="$page_team"
   pagelist[1]="$page_main"
   pagelist[2]="$page_demo"
   pagelist[3]="$page_videos"
   pagelist[4]="$page_create"

else
   error "Unsupported test page $2"
fi

#----------------------------------
# Run stress test
wget_msgs="/tmp/`basename $0`-`date +%s`.txt"
wget_msgs="wget-log"

rm -f $wget_msgs index.html*

start_time=`date`
for (( i = 1; i <= $num_requests; i++ )); do
   if [ -n "$testpage" ]; then
     submit_page="$testpage"
   else
     page_index=$[ ( $RANDOM % ${#pagelist[*]} ) ]
     submit_page=${pagelist[$page_index]}
   fi

   path=`echo $submit_page | sed "s/^.*\.org\(.*\)$/\1/"`
   echo "Sending request $i to $path"

   wget -a $wget_msgs --background $submit_page
   sleep 1
done

#----------------------------------
# Wait for all background jobs to complete
while true; do
   joblist=`ps -ef | grep wget | grep -v grep`
   if [ -z "$joblist" ]; then
      break
   fi

   sleep 1
done
end_time=`date`
echo " "

echo "Started : $start_time"
echo "Ended   : $end_time"
echo " "

sleep 3
lastfetch=`ls -t index.html* | head -1`
echo "Last file fetched is $lastfetch"

highfetch=`ls index.html* | awk -F. '{print $3}' | sort -nr | head -1`
echo "Highest file fetched is $highfetch"
echo " "

service_unavail=`grep "ERROR 503" $wget_msgs`
service_unavail_count=`grep "ERROR 503" $wget_msgs | wc -l`
if [ -z "$service_unavail" ]; then
   echo "No requests received 503 Service Unavailable"
else
   echo "$service_unavail_count requests received 503 Service Unavailable"
fi

rm -f $wget_msgs index.html*

