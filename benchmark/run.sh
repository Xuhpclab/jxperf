# CPU Cycles
LD_PRELOAD=$JXPerf_HOME/build/libpreload.so
java \
    -agentpath:$JXPerf_HOME/build/libagent.so=Generic::CYCLES:precise=2@100000 \
    -cp ./test-IrisClassifier.jar org.deeplearning4j.examples.quickstart.modeling.feedforward.classification.IrisClassifier

# Offline process -- VS Code GUI
# $JXPerf_HOME/script/process_raw_data_to_vscode.py /home/bli35/benchmarks/deeplearning4j
