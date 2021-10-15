#!/bin/bash

#launch mycroft
./start.sh

#clean file previous node id
> node_id.txt

#launch rooms simultaneously saving node id information
HiveMind-chatroom --access_key=sos-ai-etics-roo --crypto_key=oor-scite-ia-sos --name=sos-ai-etics-roo1 --host=wss://0.0.0.0 --flask-port=8010 >> node_id.txt &
HiveMind-chatroom --access_key=sos-ai-etics-ro2 --crypto_key=2or-scite-ia-sos --name=sos-ai-etics-roo2 --host=wss://0.0.0.0 --flask-port=8020 >> node_id.txt &
HiveMind-chatroom --access_key=sos-ai-etics-ro3 --crypto_key=3or-scite-ia-sos --name=sos-ai-etics-roo3 --host=wss://0.0.0.0 --flask-port=8030 >> node_id.txt