JAVA=java
INSTRUMENT=-agentpath:$JXPerf_HOME/bin/wallclock/wallClockProfile.so=start,event=wall,interval=5ms,file=profile.html
PROGRAM="$1"

"$JAVA" "$INSTRUMENT" -jar $JXPerf_HOME/benchmark/dacapo.jar -s large lusearch
