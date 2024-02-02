#!/bin/bash

list_domains=`find /etc/nginx/conf.d/ -type f -name "*.conf" -print0 | xargs -0 egrep '^(\s|\t)*server_name' | sed -r 's/(.*server_name\s*|;)//g' | tr -s ' ' '\n' | sort | uniq`

for i in ${list_domains[@]}; do
	if [[ {{server_name}} == $i ]]; then
		exit 1
	fi
done
