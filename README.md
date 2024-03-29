# JXPerf

Java inefficiency detection tool based on CPU performance monitoring counters and hardware debug registers. The tool detects dead writes, silent stores, redundant loads, and memory bloat.

![build master](https://github.com/Xuhpclab/jxperf/workflows/build%20master/badge.svg)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/c7371e45a6b84a169f3bc775893e3511)](https://www.codacy.com/gh/bolunli11/JXPerf/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bolunli11/JXPerf&amp;utm_campaign=Badge_Grade)
![license](https://img.shields.io/github/license/Xuhpclab/jxperf)

## Contents

-   [Installation](#installation)
-   [Usage](#usage)
-   [Support Platforms](#support-platforms)
-   [Support JDK Versions](#support-jdk-versions)
-   [License](#license)

## Installation

### Linux

#### 1. Installation Prerequisites

-   Install Oracle/OpenJDK and Apache Maven.
-   Install libnuma library
-   Install python modules: bintrees and google-api-python-client
-   Turn on PMU sampling in your environment:```sysctl -w kernel.perf_event_paranoid=1```
-   cp set_env.template set_env
-   Modify set_env to make JXPerf_HOME, JAVA_HOME and MAVEN_HOME point to your JXPerf, Java and Maven home.
-   source set_env

#### 2. Installation
```console
$ make
```

#### 3. Uninstallation
```console
$ make clean
```

## Usage

### Linux

#### 1. To run dead store detection
-   **Start Profiler**
```console
$ LD_PRELOAD=$JXPerf_HOME/build/preload/libpreload.so java -agentpath:$JXPerf_HOME/build/libagent.so=DeadStore::MEM_UOPS_RETIRED:ALL_STORES:precise=2@<sampling rate> -cp <classpath> <java program>
```
-   **Generate profiling results "agent-data"**
```console
$ python $JXPerf_HOME/script/process_raw_data.py
```

#### 2. To run silent store detection
-   **Start Profiler**
```console
$ LD_PRELOAD=$JXPerf_HOME/build/preload/libpreload.so java -agentpath:$JXPerf_HOME/build/libagent.so=SilentStore::MEM_UOPS_RETIRED:ALL_STORES:precise=2@<sampling rate> -cp <classpath> <java program>
```
-   **Generate profiling results "agent-data"**
```console
$ python $JXPerf_HOME/script/process_raw_data.py
```

#### 3. To run silent load detection
-   **Start Profiler**
```console
$ LD_PRELOAD=$JXPerf_HOME/build/preload/libpreload.so java -agentpath:$JXPerf_HOME/build/libagent.so=SilentLoad::MEM_UOPS_RETIRED:ALL_LOADS:precise=2@<sampling rate> -cp <classpath> <java program>
```
-   **Generate profiling results "agent-data"**
```console
$ python $JXPerf_HOME/script/process_raw_data.py
```

#### 4. To run data centric analysis
-   **Start Profiler**
```console
$ LD_PRELOAD=$JXPerf_HOME/build/preload/libpreload.so java -javaagent:$JAVA_AGENT -agentpath:$JXPerf_HOME/build/libagent.so=DataCentric::MEM_LOAD_UOPS_RETIRED:L1_MISS:precise=2@<sampling rate> -cp <classpath> <java program>
```
-   **Generate profiling results "agent-data"**
```console
$ python $JXPerf_HOME/script/process_raw_data.py
```
-   The "agent_data" includes two metrics: "Allocation Times" and "L1 Cache Misses"
    -   The metric "Allocation Times" reports allocation times for every object, which is represented with the object allocation site

    -   The metric "L1 Cache Misses" reports a pair of calling context (i.e., <allocation site, access site>) for every object incurring L1 cache misses

    -   To analyze memory bloat
        -   Identify the objects suffering from high L1 cache misses by looking into the metric "L1 Cache Misses"
        -   Check whether these objects have high allocation times by looking into the metric "Allocation Times"
        -   The objects having both high L1 cache misses and allocation times are primary optimization candidates

#### 5. To run NUMA locality analysis
-   **Start Profiler**
```console
$ LD_PRELOAD=$JXPerf_HOME/build/preload/libpreload.so java -javaagent:$JAVA_AGENT -agentpath:$JXPerf_HOME/build/libagent.so=Numa::MEM_LOAD_UOPS_RETIRED:L1_MISS:precise=2@<sampling rate> -cp <classpath> <java program>
```
-   **Generate profiling results "agent-data"**
```console
$ python $JXPerf_HOME/script/process_raw_data.py
```
-   The "agent_data" includes:
    -   "Fraction of Mismatch": mismatch times of one object over the total mismatch times of whole program
    -   "Match Times" and "Mismatch Times": the match and mismatch times of one object
    -   "Match Percentage": Match Times / (Match Times + Mismatch Times)
    -   "Mismatch Percentage": Mismatch Times / (Match Times + Mismatch Times)

#### 6. To run with generic PMU events
-   **Start Profiler**
```console
$ LD_PRELOAD=$JXPerf_HOME/build/preload/libpreload.so java -agentpath:$JXPerf_HOME/build/libagent.so=Generic::PMU_Events:precise=2@<sampling rate> -cp <classpath> <java program>
```
-   **Generate profiling results "agent-data"**
```console
$ python $JXPerf_HOME/script/process_raw_data.py
```

#### 7. To run heap profiling
-   **Start Profiler**
```console
$ LD_PRELOAD=$JXPerf_HOME/build/preload/libpreload.so java -agentpath:$JXPerf_HOME/build/libagent.so=Heap -cp <classpath> <java program>
```
-   **Generate profiling results "agent-data"**
```console
$ python $JXPerf_HOME/script/process_raw_data.py
```

#### 8. Attach to a running JVM
-   Open run_attach.sh and change MODE to one of below modes:
    -   DataCentric::MEM_LOAD_UOPS_RETIRED:L1_MISS:precise=2@sampling_rate
    -   DeadStore::MEM_UOPS_RETIRED:ALL_STORES:precise=2@sampling_rate
    -   SilentStore::MEM_UOPS_RETIRED:ALL_STORES:precise=2@sampling_rate
    -   SilentLoad::MEM_UOPS_RETIRED:ALL_LOADS:precise=2@sampling_rate
-   **Start Profiler**
```console
$ ./run_attach.sh <running time in seconds> <pid>
```

### VS Code GUI

-   In VS Code, search for ```DrCCTProf Viewer``` extension and install it
-   Generate the drcctprof format profile (test.drcctprof):```$JXPerf_HOME/script/process_raw_data_to_vscode.py <source code foler>```
-   View the test.drcctprof in VS Code:```code test.drcctprof```

## Support Platforms

We tested our tool on following platforms.

### Linux

| CPU                               | Systems           | Kernel         | Architecture |
|-----------------------------------|-------------------|----------------|--------------|
| Intel(R) Xeon(R) CPU E5-2650 v4   | Ubuntu 14.04.6    | Linux 5.1.0    | x86_64       |
| Intel(R) Xeon(R) CPU E5-2699 v3   | Ubuntu 18.04.3    | Linux 5.4.6    | x86_64       |
| Intel(R) Xeon(R) CPU E7-4830 v4   | CentOS Linux 7    | Linux 3.10.0   | x86_64       |

## Support JDK Versions

### JDK

| JDK Versions          |
|-----------------------|
| JDK 11 & later         |
| OpenJDK 11 & later     |

## License

JXPerf is released under the [MIT License](http://www.opensource.org/licenses/MIT).
