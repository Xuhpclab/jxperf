#!/usr/bin/env python2

import os
import sys
from pylib import *
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial

##global variables
isDataCentric = False
isNuma = False
isGeneric = False
isHeap = False

g_thread_context_dict = dict()
g_method_dict = dict()


def get_all_files(directory):
    files = [f for f in os.listdir(directory) if os.path.isfile(
        os.path.join(directory, f))]
    ret_dict = dict()
    for f in files:
        if f.startswith("agent-trace-") and f.find(".run") >= 0:
            start_index = len("agent-trace-")
            end_index = f.find(".run")
            tid = f[start_index:end_index]
            if tid not in ret_dict:
                ret_dict[tid] = []
            ret_dict[tid].append(os.path.join(directory, f))
    return ret_dict

def parse_input_file(file_path, level_one_node_tag):
    print(("parsing", file_path))
    with open(file_path) as f:
        contents = f.read()
        #print contents
    parser = special_xml.HomoXMLParser(level_one_node_tag, contents)
    return parser.getVirtualRoot()

def remove_all_files(directory):
    files = [f for f in os.listdir(directory) if os.path.isfile(
        os.path.join(directory, f))]
    for f in files:
        if f.startswith("agent-trace-") and f.find(".run") >= 0:
            os.remove(f)
        elif f.startswith("agent-statistics") and f.find(".run"):
            os.remove(f)

def load_method(method_root):
    method_manager = code_cache.MethodManager()
    for m_xml in method_root.getChildren():
        m = code_cache.Method(m_xml.getAttr("id"),m_xml.getAttr("version"))
        ## set fields
        m.start_line = m_xml.getAttr("start_line")
        m.file = m_xml.getAttr("file")
        m.start_addr = m_xml.getAttr("start_addr")
        m.code_size = m_xml.getAttr("code_size")
        m.method_name = m_xml.getAttr("name")
        m.class_name = m_xml.getAttr("class")

        ## add children; currently addr2line mapping and bci2line mapping
        addr2line_xml = None
        bci2line_xml = None
        for c_xml in m_xml.getChildren():
            if c_xml.name() == "addr2line":
                assert(not addr2line_xml)
                addr2line_xml = c_xml
            elif c_xml.name() == "bci2line":
                assert(not bci2line_xml)
                bci2line_xml = c_xml
        if addr2line_xml:
            for range_xml in addr2line_xml.getChildren():
                assert(range_xml.name() == "range")
                start = range_xml.getAttr("start")
                end = range_xml.getAttr("end")
                lineno = range_xml.getAttr("data")

                m.addAddr2Line(start,end,lineno)

        if bci2line_xml:
            for range_xml in bci2line_xml.getChildren():
                assert(range_xml.name() == "range")
                start = range_xml.getAttr("start")
                end = range_xml.getAttr("end")
                lineno = range_xml.getAttr("data")

                m.addBCI2Line(start,end,lineno)

        method_manager.addMethod(m)
    return method_manager


def load_context(context_root):
    context_manager = context.ContextManager()
    print("It has ", len(context_root.getChildren()), " contexts")
    for ctxt_xml in context_root.getChildren():

        ctxt = context.Context(ctxt_xml.getAttr("id"))
        # set fields
        ctxt.method_version = ctxt_xml.getAttr("method_version")
        ctxt.binary_addr = ctxt_xml.getAttr("binary_addr")
        ctxt.numa_node = ctxt_xml.getAttr("numa_node")
        ctxt.method_id = ctxt_xml.getAttr("method_id")
        ctxt.bci = ctxt_xml.getAttr("bci")
        ctxt.setParentID(ctxt_xml.getAttr("parent_id"))

        metrics_xml = None
        for c_xml in ctxt_xml.getChildren():
            if c_xml.name() == "metrics":
                assert(not metrics_xml)
                metrics_xml = c_xml
        if metrics_xml:
            for c_xml in metrics_xml.getChildren():
                attr_dict = c_xml.getAttrDict()
                id = attr_dict["id"]
                if isDataCentric:
                    if id == "0" and "value1" in attr_dict:
                        ctxt.metrics_dict["value"] = attr_dict["value1"]
                        ctxt.metrics_type = "ALLOCTIMES"
                    if id == "1" and "value1" in attr_dict:
                        ctxt.metrics_dict["value"] = attr_dict["value1"]
                        ctxt.metrics_type = "L1CACHEMISSES"
                elif isNuma:
                    if id == "1" and "value1" in attr_dict:
                        ctxt.metrics_dict["equality"] = attr_dict["value1"]
                        ctxt.metrics_type = "ALWAYS_EQUAL"
                    if id == "2" and "value1" in attr_dict:
                        ctxt.metrics_dict["inequality"] = attr_dict["value1"]
                        if "equality" in ctxt.metrics_dict:
                            ctxt.metrics_type = "EQUAL_AND_INEQUAL"
                        else:
                            ctxt.metrics_type = "ALWAYS_INEQUAL"
                else:
                    if "value1" in attr_dict:
                        assert(not("value2" in attr_dict))
                        ctxt.metrics_dict["value"] = attr_dict["value1"]
                        ctxt.metrics_type = "INT"
                    if "value2" in attr_dict:
                        assert(not("value1" in attr_dict))
                        ctxt.metrics_dict["value"] = attr_dict["value2"]
                        ctxt.metrics_type = "FP"

        ## add it to context manager
        context_manager.addContext(ctxt)
    roots = context_manager.getRoots()
    print("remaining roots: ", str([r.id for r in roots]))
    assert(len(roots) == 1)
    context_manager.getRoots()
    context_manager.populateMetrics()
    return context_manager

def output_to_file(method_manager, context_manager, dump_data, dump_data2):
    intpr = interpreter.Interpreter(method_manager, context_manager)
    if isDataCentric:
        accessed = dict()
        for ctxt_list in context_manager.getAllPaths("0", "root-leaf"):#"root-subnode"):
            i = 0
            while i < len(ctxt_list):
                if ctxt_list[i].metrics_dict:
                    key = "\n".join(intpr.getSrcPosition(c) for c in ctxt_list[:i])
                    if ctxt_list[i].metrics_type == "ALLOCTIMES" and (key in accessed) == False:
                        accessed[key] = True
                        if key in dump_data:
                            dump_data[key] += (ctxt_list[i].metrics_dict["value"])
                        else:
                            dump_data[key] = (ctxt_list[i].metrics_dict["value"])
                    elif ctxt_list[i].metrics_type == "L1CACHEMISSES":
                        if key in dump_data2:
                            dump_data2[key] += (ctxt_list[i].metrics_dict["value"])
                        else:
                            dump_data2[key] = (ctxt_list[i].metrics_dict["value"])
                i += 1
    elif isNuma:
        for ctxt_list in context_manager.getAllPaths("0", "root-leaf"):#"root-subnode"):
            if ctxt_list[-1].metrics_dict:
                key = "\n".join(intpr.getSrcPosition(c) for c in ctxt_list[:-1])
                if ctxt_list[-1].metrics_type == "ALWAYS_EQUAL":
                    if key in dump_data:
                        dump_data[key] += (ctxt_list[-1].metrics_dict["equality"])
                    else:
                        dump_data[key] = (ctxt_list[-1].metrics_dict["equality"])
                elif ctxt_list[-1].metrics_type == "ALWAYS_INEQUAL":
                    if key in dump_data2:
                        dump_data2[key] += (ctxt_list[-1].metrics_dict["inequality"])
                    else:
                        dump_data2[key] = (ctxt_list[-1].metrics_dict["inequality"])
                else :
                    if key in dump_data:
                        dump_data[key] += (ctxt_list[-1].metrics_dict["equality"])
                    else:
                        dump_data[key] = (ctxt_list[-1].metrics_dict["equality"])
                    if key in dump_data2:
                        dump_data2[key] += (ctxt_list[-1].metrics_dict["inequality"])
                    else:
                        dump_data2[key] = (ctxt_list[-1].metrics_dict["inequality"])

    else:
        for ctxt_list in context_manager.getAllPaths("0", "root-leaf"):#"root-subnode"):
            if ctxt_list[-1].metrics_dict:
                key = "\n".join(intpr.getSrcPosition(c) for c in ctxt_list[:-1])
                if ctxt_list[-1].metrics_type == "INT":
                    if key in dump_data:
                        dump_data[key] += (ctxt_list[-1].metrics_dict["value"])
                    else:
                        dump_data[key] = (ctxt_list[-1].metrics_dict["value"])
                elif ctxt_list[-1].metrics_type == "FP":
                    if key in dump_data2:
                        dump_data2[key] += (ctxt_list[-1].metrics_dict["value"])
                    else:
                        dump_data2[key] = (ctxt_list[-1].metrics_dict["value"])

def output_to_buff(method_manager, context_manager):
        intpr = interpreter.Interpreter(method_manager, context_manager)
    # if isDataCentric:
    #     accessed = dict()
    #     for ctxt_list in context_manager.getAllPaths("0", "root-leaf"):#"root-subnode"):
    #         i = 0
    #         while i < len(ctxt_list):
    #             if ctxt_list[i].metrics_dict:
    #                 key = "\n".join(intpr.getSrcPosition(c) for c in ctxt_list[:i])
    #                 print(key)
    #                 # if ctxt_list[i].metrics_type == "ALLOCTIMES" and (key in accessed) == False:
    #                 #     accessed[key] = True
    #                 #     if key in dump_data:
    #                 #         dump_data[key] += (ctxt_list[i].metrics_dict["value"])
    #                 #     else:
    #                 #         dump_data[key] = (ctxt_list[i].metrics_dict["value"])
    #                 # elif ctxt_list[i].metrics_type == "L1CACHEMISSES":
    #                 #     if key in dump_data2:
    #                 #         dump_data2[key] += (ctxt_list[i].metrics_dict["value"])
    #                 #     else:
    #                 #         dump_data2[key] = (ctxt_list[i].metrics_dict["value"])
    #             i += 1
    # elif isNuma:
    #     for ctxt_list in context_manager.getAllPaths("0", "root-leaf"):#"root-subnode"):
    #         print(ctxt_list)
    # else:
        # trace = []
        # context_manager.getFirstTrace("0", trace)

        rtraces = context_manager.getAllRtrace("0")
        print(len(rtraces))

        profile = profile_pb2.Profile()

        sample_type = profile.sample_type.add()
        profile.string_table.append("")
        profile.string_table.append("type")
        sample_type.type = len(profile.string_table) - 1
        profile.string_table.append("unit")
        sample_type.unit = len(profile.string_table) - 1

        location_id = 1
        function_id = 1
        for rtrace in rtraces:
            location = profile.location.add()
            location.id = location_id

            sample = profile.sample.add()
            sample.location_id.append(location_id)
            sample.value.append(1)
            location_id += 1
            
            print(len(rtrace))
            for trace_node in rtrace:
                if trace_node.id != 0:
                    key = intpr.getInterpreter_Context(trace_node)
                    print(key.ctype)
                    if key.ctype == 0:
                        print("root")
                    elif key.ctype == 1:
                        if key.source_lineno == "??":
                            key.source_lineno = -1
                        if key.method_start_line == "??":
                            key.method_start_line = -1
                        function = profile.function.add()
                        function.id = function_id
                        profile.string_table.append(key.method_name)
                        function.name = len(profile.string_table) - 1

                        profile.string_table.append("/Users/dolan/Desktop/test/gui/ObjectLayout/ObjectLayout/src/main/java/"+ key.source_file)
                        function.filename = len(profile.string_table) - 1
                        function.start_line = int(key.method_start_line)

                        line = location.line.add()
                        line.function_id = function_id
                        line.line = int(key.source_lineno)

                        function_id += 1
                        print("class_name:",key.class_name)
                        print("method_name:",key.method_name)
                        print("source_file:",key.source_file)
                        print("source_lineno:",key.source_lineno)
                    else:
                        print("break")
                    
                    print("-----------------")
            
        f = open("jxperf.pprof", "wb")
        f.write(profile.SerializeToString())
        f.close()
        # for ctxt_list in context_manager.getAllPaths("0", "root-leaf"):#"root-subnode"):
        #     if ctxt_list[-1].metrics_dict:
        #         key = "\n".join(intpr.getSrcPosition(c) for c in ctxt_list[:-1])
        #         print(key)
                # if ctxt_list[-1].metrics_type == "INT":
                #     if key in dump_data:
                #         dump_data[key] += (ctxt_list[-1].metrics_dict["value"])
                #     else:
                #         dump_data[key] = (ctxt_list[-1].metrics_dict["value"])
                # elif ctxt_list[-1].metrics_type == "FP":
                #     if key in dump_data2:
                #         dump_data2[key] += (ctxt_list[-1].metrics_dict["value"])
                #     else:
                #         dump_data2[key] = (ctxt_list[-1].metrics_dict["value"])

def main():
    file = open("agent-statistics.run", "r")
    result = file.read().splitlines()
    file.close()

    global isDataCentric
    global isNuma
    global isGeneric
    global isHeap
    if result[0] == 'DATACENTRIC':
        isDataCentric = True
        result = result[1:]
    elif result[0] == 'NUMA':
        isNuma = True
        result = result[1:]
    elif result[0] == 'GENERIC':
        isGeneric = True
        result = result[1:]
    elif result[0] == 'HEAP':
        isHeap = True

    ### read all agent trace files
    tid_file_dict = get_all_files(".")

    ### each file may have two kinds of information
    # 1. context; 2. code
    # the code information should be shared global while the context information is on a per-thread basis.
    xml_root_dict = dict()
    for tid in tid_file_dict:
        root = xml.XMLObj("root")
        if tid == "method":
            level_one_node_tag = "method"
        else:
            level_one_node_tag = "context"

        for f in tid_file_dict[tid]:
            new_root = parse_input_file(f, level_one_node_tag)
            root.addChildren(new_root.getChildren())
        if len(root.getChildren()) > 0:
            xml_root_dict[tid] = root

    ### reconstruct method
    print("start to load methods")
    method_root = xml_root_dict["method"]
    method_manager = load_method(method_root)
    print("Finished loading methods")

    print("Start to output")

    dump_data = dict()
    dump_data2 = dict()

    for tid in xml_root_dict:
        if tid == "method":
            continue
        print("Reconstructing contexts from TID " + tid)
        xml_root = xml_root_dict[tid]
        print("Dumping contexts from TID "+tid)
        # output_to_file(method_manager, load_context(xml_root), dump_data, dump_data2)
        output_to_buff(method_manager, load_context(xml_root))
        break

    # file = open("agent-data", "w")

    # if result and isDataCentric == False and isNuma == False and isGeneric == False and isHeap == False:
    #     assert(len(result) == 3 or len(result) == 4)
    #     deadOrRedBytes = int(result[1])

    #     if len(result) == 4 and float(result[2]) != 0.:
    #         file.write("-----------------------Precise Redundancy------------------------------\n")

    #     rows = sorted(list(dump_data.items()), key=lambda x: x[-1], reverse = True)
    #     for row in rows:
    #         file.write(row[0] + "\n\nFraction: " + str(round(float(row[-1]) * 100 / deadOrRedBytes, 2)) +"%\n")

    #     if len(result) == 4 and float(result[3]) != 0.:
    #         file.write("\n----------------------Approximate Redundancy---------------------------\n")

    #         rows = sorted(list(dump_data2.items()), key=lambda x: x[-1], reverse = True)
    #         for row in rows:
    #             file.write(row[0]  + "\n\nFraction: " +  str(round(float(row[-1]) * 100 / deadOrRedBytes, 2)) +"%\n")

    #     file.write("\nTotal Bytes: " + result[0])
    #     file.write("\nTotal Redundant Bytes: " + result[1])
    #     if len(result) == 4:
    #         file.write("\nTotal Redundancy Fraction: " + str(round((float(result[2]) + float(result[3])) * 100, 2)) + "%")
    #     else:
    #         file.write("\nTotal Redundancy Fraction: " + str(round(float(result[2]) * 100, 2)) + "%")
    # elif result and isDataCentric == True:
    #     assert(len(result) == 2)
    #     allocTimes = int(result[0])
    #     l1CacheMisses = int(result[1])
    #     if allocTimes != 0:
    #         file.write("-----------------------Allocation Times------------------------------\n")

    #         rows = sorted(list(dump_data.items()), key=lambda x: x[-1], reverse = True)
    #         for row in rows:
    #             file.write(row[0] + "\n\nFraction: " + str(round(float(row[-1]) * 100 / allocTimes, 2)) +"%\n")

    #     if l1CacheMisses != 0:
    #         file.write("\n-----------------------L1 Cache Misses------------------------------\n")

    #         rows = sorted(list(dump_data2.items()), key=lambda x: x[-1], reverse = True)
    #         for row in rows:
    #             file.write(row[0]  + "\nFraction: " +  str(round(float(row[-1]) * 100 / l1CacheMisses, 2)) +"%\n")
    #     file.write("\nTotal Allocation Times: " + result[0])
    #     file.write("\nTotal L1 Cache Misses: " + result[1])
    # elif result and isNuma == True:
    #     assert(len(result) == 2)
    #     totalEqualityTimes = int(result[0])
    #     totalInequalityMismatches = int(result[1])
    #     if (totalInequalityMismatches != 0):
    #         rows = sorted(list(dump_data.items()), key=lambda x: x[-1], reverse = True)
    #         for row in rows:
    #             inequalityTimes = row[-1]
    #             equalityTimes = 0
    #             if row[0] in dump_data2:
    #                 equalityTimes = dump_data2[row[0]]
    #             file.write(row[0] + "\n\nFraction of Mismatch: " + str(round(float(inequalityTimes) * 100 / totalInequalityMismatches, 2)) + "%;" + " Match Times: " + str(equalityTimes) + " Mismatch Times: " + str(inequalityTimes) + " Match Percentage: " + str(round(float(equalityTimes) * 100 / (equalityTimes + inequalityTimes), 2)) + "%;" + " Mismatch Percentage: " + str(round(float(inequalityTimes) * 100 / (equalityTimes + inequalityTimes), 2)) + "%\n")
    #     file.write("\nTotal Match Times: " + result[0])
    #     file.write("\nTotal Mismatch Times: " + result[1])
    # elif isGeneric == True:
    #     file.write("-----------------------Generic Counter------------------------------\n")

    #     rows = sorted(list(dump_data.items()), key=lambda x: x[-1], reverse = True)

    #     for row in rows:
    #         if row[0] != "":
    #             file.write(row[0] + "\n\nGeneric Counter: " + str(float(row[-1])) +"\n")
    # elif isHeap == True:
    #     file.write("-----------------------Heap Analysis------------------------------\n")

    #     rows = sorted(list(dump_data.items()), key=lambda x: x[-1], reverse = True)

    #     for row in rows:
    #         if row[0] != "":
    #             file.write(row[0] + "\n\nObject allocation size: " + str(row[-1]) +"bytes\n")

    # file.close()

    print("Final dumping")

    # remove_all_files(".")

main()
