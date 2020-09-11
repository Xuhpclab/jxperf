#!/usr/bin/env python2

import os, sys
from pylib import *
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
import Tkinter as tk #import Tkinter as tk #change to commented for python2
import ttk
import Tkinter, Tkconstants, tkFileDialog
import re
import math

##global variables
isDataCentric = False

g_thread_context_dict = dict()
g_method_dict = dict()

def insertTab(file_dict, cur_item):
	selected_file = tree.item(cur_item, "text")
	item_text = re.search('\(([^)]+)', selected_file).group(1)
	filename = item_text.split(":")[0]
	if file_dict.has_key(filename) and (filename in tab_list) == False:
		filePath = file_dict[filename]
	else:
		return
	tab = tk.Frame(master = tabBar)
	tabBar.add(tab, text = filename, state = "hidden")
	textContainer = ttk.Labelframe(master = tab)
	textContainer.pack(expand = True, fill = "both")
	textArea = tk.Text(master = textContainer)
	textArea.pack(side = "left", expand = True, fill = "both")
	text_list.append(textArea)
	tab_list.append(filename)
	f = open(filePath, mode = "r")
	line_num = 1
	while True:
		line = f.readline()
		if not line: break
		num_digit = len(str(line_num))
		space = ""
		for k in range(num_digit, 5):
			space = space + " "
		textArea.insert("insert",str(line_num) + space + line)
		line_num = line_num + 1
	textArea.configure(state = "disabled")
	f.close()
	scrollBar = tk.Scrollbar(master = textContainer)
	scrollBar.pack(side = "right", fill = "y")
	scrollBar.config(command = textArea.yview)
	textArea.config(yscrollcommand = scrollBar.set)

def OnDoubleClick(event):
	cur_tab = ""
	item = tree.selection()[0]
	selected_file = tree.item(item, "text")
	item_text = re.search('\(([^)]+)', selected_file).group(1)
	line_start = item_text.split(":")[1] + ".0"
	filename = item_text.split(":")[0]
	tab_index = tab_list.index(filename)
	tabBar.select(tab_index)
	textArea = text_list[tab_index]
	line_end = textArea.index("%s lineend" % line_start)
	cur_tab = tabBar.tab(tabBar.select(), "text")
	textArea.configure(state = "normal")
	textArea.mark_set("insert", line_start)
	textArea.see("insert")
	textArea.tag_remove("highlight", 1.0, "end")
	textArea.tag_add("highlight", line_start, line_end)
	textArea.tag_configure("highlight", background = "yellow")
	textArea.configure(state = "disabled")

"""
def Error_frame():
	top = tk.Toplevel()
	top.title("Error")
	lbl = tk.Label(top, text = "Error: Unmatch between the selected tab and entry!", font = "24").pack()
"""

#GUI widgets
win = tk.Tk()
win.geometry("800x600")

tabBar = ttk.Notebook(master = win, height = 10)
tabBar.pack(expand = True, fill = "both")
text_list = []
tab_list = []
#menuBar = tk.Menu(master = win)
#win.configure(menu = menuBar)
#filemenu = tk.Menu(master = menuBar, tearoff = 0)
#menuBar.add_cascade(label = "File", menu = filemenu)
#filemenu.add_command(label = "open", command = openFile)

tree_style = ttk.Style()
tree_style.configure("Treeview", indent = 5)
tree=ttk.Treeview(win, style = "Treeview")

tree["columns"]=("one", "two")
tree.column("#0", width=600, minwidth=250)
tree.column("one", width=100, minwidth=0)
tree.column("two", width=100, minwidth=0)

tree.heading("#0",text="Scope",anchor=tk.W)
tree.heading("one", text="L1 Cache miss(%)",anchor=tk.W)
tree.heading("two", text="Allocation times",anchor=tk.W)

def get_all_files(directory):
	files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory,f))]
	ret_dict = dict()
	for f in files:
		if f.startswith("agent-trace-") and f.find(".run") >= 0:
			start_index = len("agent-trace-")
			end_index = f.find(".run")
			tid = f[start_index:end_index]
			if tid not in ret_dict:
				ret_dict[tid] = []
			ret_dict[tid].append(os.path.join(directory,f))
	return ret_dict

def parse_input_file(file_path, level_one_node_tag):
	print "parsing", file_path
	with open(file_path) as f:
		contents = f.read()
		#print contents
	parser = special_xml.HomoXMLParser(level_one_node_tag, contents)
	return parser.getVirtualRoot()

def remove_all_files(directory):
	files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory,f))]
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

				m.addAddr2Line((start,end),lineno)

		if bci2line_xml:
			for range_xml in bci2line_xml.getChildren():
				assert(range_xml.name() == "range")
				start = range_xml.getAttr("start")
				end = range_xml.getAttr("end")
				lineno = range_xml.getAttr("data")

				m.addBCI2Line((start,end),lineno)

		method_manager.addMethod(m)
	return method_manager

def load_context(context_root):
	context_manager = context.ContextManager()
	print "It has ", len(context_root.getChildren()), " contexts"
	for ctxt_xml in context_root.getChildren():

		ctxt = context.Context(ctxt_xml.getAttr("id"))
		# set fields
		ctxt.method_version = ctxt_xml.getAttr("method_version")
		ctxt.binary_addr = ctxt_xml.getAttr("binary_addr")
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
					if id == "0" and attr_dict.has_key("value1"):
				    		ctxt.metrics_dict["value"] = attr_dict["value1"]
				    		ctxt.metrics_type = "ALLOCTIMES"
					elif id == "1" and attr_dict.has_key("value1"):
				    		ctxt.metrics_dict["value"] = attr_dict["value1"]
				    		ctxt.metrics_type = "L1CACHEMISSES"
				else:
					if attr_dict.has_key("value1"):
				    		assert(not(attr_dict.has_key("value2")))
				    		ctxt.metrics_dict["value"] = attr_dict["value1"]
				    		ctxt.metrics_type = "INT"
					if attr_dict.has_key("value2"):
				    		assert(not(attr_dict.has_key("value1")))
				    		ctxt.metrics_dict["value"] = attr_dict["value2"]
				    		ctxt.metrics_type = "FP"

		## add it to context manager
		context_manager.addContext(ctxt)
	roots = context_manager.getRoots()
	print "remaining roots: ", str([r.id for r in roots])
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
					key = "\n".join(intpr.getSrcPosition(c, isDataCentric) for c in ctxt_list[:i])
					if ctxt_list[i].metrics_type == "ALLOCTIMES" and accessed.has_key(key) == False:
						accessed[key] = True
						if dump_data.has_key(key):
							dump_data[key] += (ctxt_list[i].metrics_dict["value"])
						else:
							dump_data[key] = (ctxt_list[i].metrics_dict["value"])
					elif ctxt_list[i].metrics_type == "L1CACHEMISSES":
						if dump_data2.has_key(key):
							dump_data2[key] += (ctxt_list[i].metrics_dict["value"])
						else:
							dump_data2[key] = (ctxt_list[i].metrics_dict["value"])
				i += 1
	else:
		for ctxt_list in context_manager.getAllPaths("0", "root-leaf"):#"root-subnode"):
			if ctxt_list[-1].metrics_dict:
				key = "\n".join(intpr.getSrcPosition(c) for c in ctxt_list[:-1])
				if ctxt_list[-1].metrics_type == "INT":
					if dump_data.has_key(key):
						dump_data[key] += (ctxt_list[-1].metrics_dict["value"])
					else:
						dump_data[key] = (ctxt_list[-1].metrics_dict["value"])
				elif ctxt_list[-1].metrics_type == "FP":
					if dump_data2.has_key(key):
						dump_data2[key] += (ctxt_list[-1].metrics_dict["value"])
					else:
						dump_data2[key] = (ctxt_list[-1].metrics_dict["value"])

def main():

	file = open("agent-statistics.run", "r")
	result = file.read().splitlines()
	file.close()

	global isDataCentric
	if result[0] == 'DATACENTRIC':
		isDataCentric = True
		result = result[1:]

	file_dict = {}
	file_path = str(sys.argv[1])
	for dirpath, dirs, files in os.walk(file_path):
		for filename in files:
			fname = os.path.join(dirpath,filename)
			file_dict[filename] = fname

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
	 	output_to_file(method_manager, load_context(xml_root), dump_data, dump_data2)

	file = open("agent-data", "w")

	if result and isDataCentric == False:
		assert(len(result) == 3 or len(result) == 4)
		deadOrRedBytes = long(result[1])

		if len(result) == 4 and float(result[2]) != 0.:
			file.write("-----------------------Precise Redundancy------------------------------\n")

			rows = sorted(dump_data.items(), key=lambda x: x[-1], reverse = True)
			for row in rows:
				file.write(row[0] + "\n\nFraction: " + str(round(float(row[-1]) * 100 / deadOrRedBytes, 2)) +"%\n")

		if len(result) == 4 and float(result[3]) != 0.:
			file.write("\n----------------------Approximate Redundancy---------------------------\n")

			rows = sorted(dump_data2.items(), key=lambda x: x[-1], reverse = True)
			for row in rows:
				file.write(row[0]  + "\n\nFraction: " +  str(round(float(row[-1]) * 100 / deadOrRedBytes, 2)) +"%\n")

		file.write("\nTotal Bytes: " + result[0])
		file.write("\nTotal Redundant Bytes: " + result[1])
		if len(result) == 4:
			file.write("\nTotal Redundancy Fraction: " + str(round((float(result[2]) + float(result[3])) * 100, 2)) + "%")
		else:
			file.write("\nTotal Redundancy Fraction: " + str(round(float(result[2]) * 100, 2)) + "%")
	elif result:
		assert(len(result) == 2)
		allocTimes = long(result[0])
		l1CacheMisses = long(result[1])
		alloc_dict = {}
		if allocTimes != 0:
			file.write("-----------------------Allocation Times------------------------------\n")

			rows = sorted(dump_data.items(), key=lambda x: x[-1], reverse = True)
			for row in rows:
				file.write(row[0] + "\n\nFraction: " + str(round(float(row[-1]) * 100 / allocTimes, 2)) +"%\n")
				key = row[0].replace("\n", "")
				alloc_dict[key] = str(round(float(row[-1]) * 100 / allocTimes, 2))

		if l1CacheMisses != 0:
			file.write("\n-----------------------L1 Cache Misses------------------------------\n")

			rows = sorted(dump_data2.items(), key=lambda x: x[-1], reverse = True)
			part2_counter = 0
			for row in rows:
				file.write(row[0]  + "\nFraction: " +  str(round(float(row[-1]) * 100 / l1CacheMisses, 2)) +"%\n")
				tree_items = row[0].splitlines()
				first_in_part2 = True
				part = "1"
				i = 0
				while i < (len(tree_items) - 1):
					i = i + 1
					if tree_items[i] == "":
						continue
					if tree_items[i] == "com.google.monitoring.runtime.instrumentation.AllocationRecorder.recordAllocation(AllocationRecorder.java:238)":
						i = i + 3
						part = "2"
						continue
					elif part == "1":
						if tree.exists(tree_items[i]):
							cur_id = tree_items[i]
							key = row[0].split("*")[0].replace("\n","")
							new_value_2 = str(int(float(tree.item(tree_items[i])["values"][1]) + (float(alloc_dict[key]) * int(result[0]) / 10000000)))
							tree.set(tree_items[i], column = "two", value = new_value_2)
							new_value_1 = str(float(tree.item(tree_items[i])["values"][0]) + (round(float(row[-1]) * 100 / l1CacheMisses, 2)))
							if math.ceil(float(new_value_1)) >= 98:
								new_value_1 = "100.00"
							tree.set(tree_items[i], column = "one", value = new_value_1)
							continue
						if i == 1:
							key = row[0].split("*")[0].replace("\n","")
							tree.insert("", "end", tree_items[i], text=tree_items[i], values=(str(round(float(row[-1]) * 100 / l1CacheMisses, 2)), str(float(alloc_dict[key]) * int(result[0]) / 10000000)), tags = "part1")
							cur_id = tree_items[i]
							insertTab(file_dict, tree_items[i])
						else:
							key = row[0].split("*")[0].replace("\n","")
							tree.insert(tree_items[i-1], "end", tree_items[i], text=tree_items[i], values=(str(round(float(row[-1]) * 100 / l1CacheMisses, 2)), str(int(float(alloc_dict[key]) * int(result[0]) / 10000000))), tags = "part1")
							cur_id = tree_items[i]
							insertTab(file_dict, tree_items[i])
					elif part == "2":
						if first_in_part2:
							part2_counter = part2_counter + 1
							parent_id = tree_items[i-5]
							item_id = tree_items[i] + cur_id + str(part2_counter)
							tree.insert(parent_id, "end", item_id, text=tree_items[i], values=(str(round(float(row[-1]) * 100 / l1CacheMisses, 2)), "Non"), tags = "part2")
							first_in_part2 = False
							insertTab(file_dict, tree_items[i])
						else:
							if tree.exists(tree_items[i] + cur_id + str(part2_counter)):
								part2_counter = part2_counter + 1
								parent_id = tree_items[i-1] + cur_id + str(part2_counter-1)
								item_id = tree_items[i] + cur_id + str(part2_counter)
								tree.insert(parent_id, "end", item_id, text=tree_items[i], values=(str(round(float(row[-1]) * 100 / l1CacheMisses, 2)), "Non"), tags = "part2")
								insertTab(file_dict, item_id)
							else:
								parent_id = tree_items[i-1] + cur_id + str(part2_counter)
								item_id = tree_items[i] + cur_id + str(part2_counter)
								tree.insert(parent_id, "end", item_id, text=tree_items[i], values=(str(round(float(row[-1]) * 100 / l1CacheMisses, 2)), "Non"), tags = "part2")
								insertTab(file_dict, item_id)
		file.write("\nTotal Allocation Times: " + result[0])
		file.write("\nTotal L1 Cache Misses: " + result[1])

	file.close()
	tree.tag_configure("part1", foreground = "red")
	tree.tag_configure("part2", foreground = "blue")
	tree.pack(fill='both', expand = True)
	tree.bind("<Double-1>", OnDoubleClick)
	win.mainloop()
	print("Final dumping")

	#remove_all_files(".")

main()
