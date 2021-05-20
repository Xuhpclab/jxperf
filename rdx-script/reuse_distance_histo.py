#!/usr/bin/env python3

import argparse
from pylib import *
import subprocess
## tunable parameters
g_length_per_percent = 2

g_time_distance_range_plan = None
g_stack_distance_range_plan = None

num_accesses = 0
num_elements = 0


def draw_histo(markers:list, counts:list)->None:
	print(len(markers), len(counts))
	assert(len(markers) == len(counts))
	if len(markers) == 0: return
	#all_counts = sum(counts)
	#percent_counts = [ counts[i]/all_counts * 100.0 for i in range(0, len(counts))]
	percent_counts = [counts[i]*100.0 for i in range(0, len(counts))]
	print(percent_counts)
	for i in range(0, len(markers)):
		print("-"*int(round(g_length_per_percent* percent_counts[i]))," ", round(percent_counts[i],1),"%", sep="", end="")
		print("  ", markers[i], sep="")

def report_collection(range_list, fraction_list):

	markers = [ "["+"{:.2E}".format(r[0])+","+"{:.2E}".format(r[1])+")"  for r in range_list] ## convert to scientific notation

	draw_histo(markers, fraction_list)


def process_input(input_file, output):
	reading_result = {"file_type": "rdx"}

	reuse_histo = {}
	rdx_file = open("rdx.run")
	for line in rdx_file:
		key, value = line.split()
		reuse_histo[int(key)] = int(value)

	if reading_result["file_type"] == "rdx":
		reuse_histo = calibration.hpcrun_calibration(reuse_histo, "10M")


	if g_time_distance_range_plan.startswith("F,"):
		time_range_list =  config.time_distance_range_list(g_time_distance_range_plan.split(",")[1])
		time_intervals = [ r[0] for r in time_range_list] +[ time_range_list[-1][1] ]
		print(time_intervals)
		histo = reuse_model.Histogram(reuse_histo, time_intervals, None, None)
	elif g_time_distance_range_plan.startswith("D,"):
		first_term, ratio = list(map(float, g_time_distance_range_plan.split(",")[1:] ))
		histo = reuse_model.Histogram(reuse_histo, None, first_term, ratio)
	else: ## no such plan
		assert(False)

	model = reuse_model.Tdh2RdhModelExt(histo, num_elements , num_accesses)
	print("g_stack_distance_range_plan", g_stack_distance_range_plan)
	stack_range_list =  config.stack_distance_range_list(g_stack_distance_range_plan)
	stack_intervals = [ r[0] for r in stack_range_list] +[ stack_range_list[-1][1] ]
	histo = reuse_model.Histogram({0:1}, stack_intervals, None, None)

	stack_distance_range_list = histo.getRanges()
	rdh = model.getRdh(stack_distance_range_list)
	report_collection(stack_distance_range_list, rdh)

	with open(output, "w") as f:
		for r, b in zip(stack_distance_range_list, rdh):
			f.write(" ".join([str(r[0]),str(r[1]), str(b)])+"\n")

def main():
	global num_accesses
	global num_elements
    
	file_memory_usage = open("maxMem.run", "r")
	result_memory_usage = file_memory_usage.read().splitlines()
	file_memory_usage.close()
	num_elements = int(result_memory_usage[-1]) * 1024 // 16
	print(num_elements)

	file = open("agent-statistics.run", "r")
	result = file.read().splitlines()
	file.close()
	result = result[1:]
	num_accesses = int(result[0]) / 1
	print(num_accesses)

	parser = argparse.ArgumentParser()
	parser.add_argument("input_file", help="the path to the hpcrun or time reuse data file")
	parser.add_argument("-o", "--output", default=None, help="Specify the name of the bin output file")
	parser.add_argument("--trh-plan", default="F,L3", help="The ways of bins for splitting time reuse histogram")
	parser.add_argument("--srh-plan", default="L3", help="The ways of bins for splitting stack reuse histogram")


	args = parser.parse_args()

	if args.output:
		output = args.output
	else:
		output = args.input_file + ".bin"

	global g_time_distance_range_plan, g_stack_distance_range_plan
	g_time_distance_range_plan = args.trh_plan
	g_stack_distance_range_plan = args.srh_plan

	process_input(args.input_file, output)

main()
