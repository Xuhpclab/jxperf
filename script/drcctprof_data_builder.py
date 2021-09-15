import os
from pylib import profile_pb2 as drcctprof_profile

class StringTable:
    def __init__(self, profile:drcctprof_profile.Profile):
        self.table = {"": 0}
        self.maxIndex = 0
        self.profile = profile
        self.profile.string_table.append("")

    def addString(self, temp_str):
        if temp_str in self.table.keys():
            return self.table[temp_str]
        self.maxIndex += 1
        self.table[temp_str] = self.maxIndex
        self.profile.string_table.append(temp_str)
        # print(temp_str + ":" + str(self.maxIndex) + ":" + self.profile.string_table[self.maxIndex])
        return self.maxIndex
    
    def getTableSize(self):
        return self.maxIndex
    
    def getString(self, index):
        if index >= self.maxIndex:
            return ""
        return self.profile.string_table[index]

class SouceFileTable:
    def __init__(self, profile:drcctprof_profile.Profile):
        self.profile = profile
        self.table = {}
    
    def addSourceFile(self, fileNameIndex, filePathIndex, type):
        if filePathIndex in self.table.keys():
            return self.table[filePathIndex]
        sourceFile = self.profile.source_file.add()
        sourceFile.id = filePathIndex
        sourceFile.filename = fileNameIndex
        sourceFile.location_path = filePathIndex
        sourceFile.type = type
        self.table[filePathIndex] = sourceFile
        return sourceFile

class FunctionTableKey:
    def __init__(self, file_path, name):
        self.file_path = file_path
        self.name = name

    def __eq__(self, other):
        return self.file_path == self.file_path and  self.name == self.name
    
    def __hash__(self):
        return hash(str(self.file_path) + ";" + str(self.name))

class FunctionTable:
    def __init__(self, profile:drcctprof_profile.Profile):
        self.profile = profile
        self.table = {}
        self.maxIndex = 0
    
    def addFunction(self, sourceFile:drcctprof_profile.SourceFile, name, system_name, start_line):
        key = FunctionTableKey(sourceFile.filename, name)
        if key in self.table.keys():
            return self.table[key]
        function = self.profile.function.add()
        function.id = self.maxIndex
        function.name = name
        function.system_name = system_name
        function.start_line = start_line
        function.source_file_id = sourceFile.id
        self.table[key] = function
        self.maxIndex += 1
        return function

class LocationTableKey:
    def __init__(self, functionId, lineNo):
        self.functionId = functionId
        self.lineNo = lineNo

    def __eq__(self, other):
        return self.functionId == self.functionId and  self.lineNo == self.lineNo
    
    def __hash__(self):
        return hash(str(self.functionId) + ";" + str(self.lineNo))

class LocationTable:
    def __init__(self, profile):
        self.profile = profile
        self.table = {}
        self.maxIndex = 0

    def addLocation(self, function:drcctprof_profile.Function, lineNo):
        key = LocationTableKey(function.id, lineNo)
        if key in self.table.keys():
            return self.table[key]
        location = self.profile.location.add()
        location.id = self.maxIndex
        line = location.line.add()
        line.function_id = function.id
        line.line = lineNo
        self.table[key] = location
        self.maxIndex += 1
        return location

class Context:
    def __init__(self, dcontext:drcctprof_profile.Context):
        self.dcontext = dcontext
        self.childrenSet = {}
    
    def addChild(self, childDontext:drcctprof_profile.Context):
        if childDontext.id in self.childrenSet.keys():
            return self.childrenSet[childDontext.id]
        self.dcontext.children_id.append(childDontext.id)
        childContext = Context(childDontext)
        self.childrenSet[childDontext.id] = childContext
        return childContext

    def getId(self):
        return self.dcontext.id

class ContextTable:
    def __init__(self, profile:drcctprof_profile.Profile):
        self.profile = profile
        self.table = {}
    
    def addContext(self, contextId, location:drcctprof_profile.Location, parentContext:Context):
        key = contextId
        if key in self.table.keys():
            return self.table[key]
        dcontext = self.profile.context.add()
        dcontext.id = contextId
        dcontext.location_id = location.id
        if parentContext is None:
            dcontext.parent_id = 0
            self.table[key] = Context(dcontext)
        else:
            dcontext.parent_id = parentContext.getId()
            self.table[key] = parentContext.addChild(dcontext)
        return self.table[key]

class ContextMsg:
    def __init__(self, contextId, filePath, name, system_name, start_line, lineNo):
        self.contextId = contextId
        self.filePath = filePath
        self.name = name
        self.system_name = system_name
        self.start_line = start_line
        self.lineNo = lineNo

class MetricMsg:
    def __init__(self, intValue, uintValue, strValue):
        self.intValue = intValue
        self.uintValue = uintValue
        self.strValue = strValue

class Profile:
    def __init__(self, drcctprofProfile:drcctprof_profile.Profile):
        self.drcctprofProfile = drcctprofProfile

        self.stringTable = StringTable(self.drcctprofProfile)
        self.souceFileTable = SouceFileTable(self.drcctprofProfile)
        self.functionTable = FunctionTable(self.drcctprofProfile)
        self.locationTable = LocationTable(self.drcctprofProfile)
        self.contextTable = ContextTable(self.drcctprofProfile)

    def addMetricType(self, value_type, unit, des):
        metric_type = self.drcctprofProfile.metric_type.add()
        metric_type.value_type = value_type
        metric_type.unit = self.stringTable.addString(unit)
        # print("metric_type.unit" + str(metric_type.unit))
        metric_type.des = self.stringTable.addString(des)
    
    def addSouceFile(self, fileName, filePath, type):
        return self.souceFileTable.addSourceFile(self.stringTable.addString(fileName), self.stringTable.addString(filePath), type)
    
    def addFunction(self, filePath, name, system_name, start_line):
        return self.functionTable.addFunction(self.addSouceFile(filePath, filePath, 0), self.stringTable.addString(name), self.stringTable.addString(system_name), start_line)

    def addLocation(self, filePath, name, system_name, start_line, lineNo):
        return self.locationTable.addLocation(self.addFunction(filePath, name, system_name, start_line), lineNo)

    def addContext(self, contextId, filePath, name, system_name, start_line, lineNo, parentContext:Context):
        return self.contextTable.addContext(contextId, self.addLocation(filePath, name, system_name, start_line, lineNo), parentContext)
    
    def addContextFromMsg(self, contextMsg:ContextMsg, parentContext:Context):
        return self.addContext(contextMsg.contextId, contextMsg.filePath, contextMsg.name, contextMsg.system_name, contextMsg.start_line, contextMsg.lineNo, parentContext)

    def addSample(self, contextMsgList:[], metricList:[]):
        curContext = None
        # for contextMsg in reversed(contextMsgList):
        for contextMsg in contextMsgList:
            curContext = self.addContextFromMsg(contextMsg, curContext)
        if curContext != None:
            sample = self.drcctprofProfile.sample.add()
            sample.context_id = curContext.getId()
            for metricMsg in metricList:
                metric = sample.metric.add()
                metric.int_value = int(metricMsg.intValue)
                metric.uint_value = int(metricMsg.uintValue)
                metric.str_value = self.stringTable.addString(metricMsg.strValue)

            return sample
        return None

    def serializeToString(self):
        return self.drcctprofProfile.SerializeToString()


class Builder:

    def __init__(self):
        self.profile = Profile(drcctprof_profile.Profile())

    def generateProfile(self, fileFullPath):
        f = open(fileFullPath, "wb")
        f.write(self.profile.serializeToString())
        f.close()
        print("generate drcctprof data file at " + os.path.abspath(fileFullPath))

    def addMetricType(self, value_type, unit, des):
        self.profile.addMetricType(value_type, unit, des)

    def addSample(self, contextMsgList:[], metricList:[]):
        self.profile.addSample(contextMsgList, metricList)
    



