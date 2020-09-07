#!/bin/bash

ATTACH=$JXPerf_HOME/bin/jattach/attach
MODE=DataCentric::MEM_LOAD_UOPS_RETIRED:L1_MISS:precise=2@1000000
PID="$1"
DURATION="$2"
LOAD=load
INSTRUMENT=instrument
TRUE_FLAG=true
FALSE_FLAG=false
JVMTI_AGENT_START=$JXPerf_HOME/build/libagent.so
JVMTI_AGENT_STOP=$JXPerf_HOME/build/libstop.so

"$ATTACH" "$PID" "$LOAD" "$INSTRUMENT" "$FALSE_FLAG" $JAVA_AGENT
"$ATTACH" "$PID" "$LOAD" "$JVMTI_AGENT_START" "$TRUE_FLAG" "$MODE"s
while (( DURATION-- > 0 ))
do
    sleep 1
done
"$ATTACH" "$PID" "$LOAD" "$JVMTI_AGENT_STOP" "$TRUE_FLAG" "$MODE"p
