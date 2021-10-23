#!/bin/bash


#get id from text file...NB: Only works if only id in text file...ELse copy and replace
#id1=$(cat node_id_1.txt)
#id2=$(cat node_id_2.txt)

#kill the nodes
top
ps -aux | grep hivemind-chatro
#The command ps -ax displays yours as well as other users' processes.
#grep matches lines which match a regular expression. In this case, the regular expression is $$, which the shell will expand to the process ID of the current shell.
#kill -INT $id1
kill -INT $id2

#launch mycroft
./start.sh

#clean file previous node id
> node_id_1.txt
> node_id_2.txt
> node_id_3.txt


#launch rooms simultaneously saving node id information
HiveMind-chatroom --access_key=sos-ai-etics-roo --crypto_key=oor-scite-ia-sos --name=sos-ai-etics-roo1 --host=wss://0.0.0.0 --flask-port=8010 >> node_id_1.txt &
HiveMind-chatroom --access_key=sos-ai-etics-ro2 --crypto_key=2or-scite-ia-sos --name=sos-ai-etics-roo2 --host=wss://0.0.0.0 --flask-port=8020 >> node_id_2.txt &
HiveMind-chatroom --access_key=sos-ai-etics-ro3 --crypto_key=3or-scite-ia-sos --name=sos-ai-etics-roo3 --host=wss://0.0.0.0 --flask-port=8030 >> node_id_3.txt