# JXPerf

Java inefficiency detection tool based on CPU performance monitoring counters and hardware debug registers. The tool detects dead writes, silent stores, redundant loads, and memory bloat.

![build master](https://github.com/Xuhpclab/jxperf/workflows/build%20master/badge.svg)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/42f3be52e8a04bd19f3be986f660600e)](https://app.codacy.com/gh/Xuhpclab/jxperf?utm_source=github.com&utm_medium=referral&utm_content=Xuhpclab/jxperf&utm_campaign=Badge_Grade_Dashboard)
![license](https://img.shields.io/github/license/Xuhpclab/jxperf)

## Contents

- [Installation](#installation)
- [Usage](#usage)
- [Support Platforms](#support-platforms)
- [Support JDK Versions](#support-jdk-versions)
- [License](#license)

## Installation

### Linux

#### 1. Installation Prerequisites

* Install Oracle/OpenJDK and Apache Maven.
* cp set_env.template set_env
* Modify set_env to make JXPerf_HOME, JAVA_HOME and MAVEN_HOME point to your JXPerf, Java and Maven home.
* source set_env

#### 2. Installation
```console
$ make
```

#### 2. Uninstallation
```console
$ make clean
```
