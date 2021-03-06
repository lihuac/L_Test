#!/usr/bin/env python
from __future__ import print_function
import serial
import re
import os
import datetime
import time
import subprocess

testlist_file = 'lh_testlist.txt'
#testlist_file = 'part7_testlist.txt'
serial_number = '1234567'
testcfg_file  = 'test.cfg'
templogfile   = 'temp.log'
templastlogfile = 'templast.log'
directory     = 'log'
lastlog       = ''
test_start    = datetime.datetime.now()
test_time     = str(test_start)[:19]
final_result  = 1					    # initial fail
SERIAL_CMD    = 1
LINUX_CMD     = 0
retry_time    = 0
cwd           = os.getcwd()

dic_config    = {}
test_array    = []
port_array    = []

LOG           = open(templogfile, "w")
TEMP_LAST_LOG = open(templastlogfile, "w")


class Test:
	test_description = ""
	test_path        = ""
	command          = ""
	pass_phrase      = ""
	fail_phrase      = ""
	timeout          = 0
	retry            = 0

# Test MAIN	
def main():
	read_config()
	#printing_testcfg()
	tmp = ''
	parse_testlist(testlist_file, tmp)
	printing()
	#create_sn_file()
	initiate_logging()
	run_testlist()
	print_result()
	print_test_duration()
	mv_log()
	
def execute_linux_cmd(test_index):
	console_log_print("Linux Test for test item " + str(test_index) + "\n\n")
	path = test_array[test_index].test_path
	cmd  = test_array[test_index].command
	status = 1
	print ("start linux command")
	if path != '':
		print ("change directory")
		os.chdir(path)
	if cmd != '':
		p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
		status = check_result(test_index, LINUX_CMD, p)
	else:
		status = check_result(test_index, LINUX_CMD, 0)
		
	print ("linux: " + path+" " +cmd)
	return status
	
def execute_serial_cmd(test_index):
	console_log_print("Serial Test for test item " + str(test_index) + "\n\n")
	ser = init_serial_port(test_index)
	msg = test_array[test_index].command+"\n"
	ser.write(msg)
	#time.sleep(30)
	result = check_result(test_index, SERIAL_CMD, ser)
	return result

def close_ports():
	for i in range(len(port_array)):
		port_array[i].close()
	
def init_serial_port(test_index):
	path = test_array[test_index].test_path
	tmp = path.split('_')
	path = "/dev/"+tmp[0]
	for i in range(len(port_array)):
		if path == port_array[i].name:
			return port_array[i]
	speed = int(tmp[1])
	ser = serial.Serial(
		port=path, 
		baudrate=speed, 
		parity=serial.PARITY_NONE,
		stopbits=serial.STOPBITS_ONE,
		bytesize=serial.EIGHTBITS,
		timeout=1,
		rtscts=False
	)
	port_array.append(ser)
	return ser

def check_result(index, cmd_type, ref_port):
	name          = test_array[index].test_description
	pass_word     = test_array[index].pass_phrase
	fail_word     = test_array[index].fail_phrase
	time_out      = int(test_array[index].timeout)
	#retry_time    = test_array[index].retry
	temp          = ''
	output        = ''
	isTestTimeOut = True
	pass_test     = 0
	ser           = ref_port
	test_start = time.time()
	test_cur = time.time()
	while(1):
		if time_out > 0 and test_cur - test_start > time_out:
			break
		#time.sleep(1)
		
		if cmd_type == SERIAL_CMD:
			temp = ''
			reading = (str(ser.readline()))
			if len(reading)>0:
				temp = reading
			
			
		if cmd_type == LINUX_CMD and ser!=0:
			temp = ''
			reading = ser.stdout.read(255)
			if reading !='':
				temp = reading
		
		
		output = output + temp
		console_log_print(temp)
		
		if pass_word != '':
			#if pass_word in output:
			if re.search(pass_word, output):
				pass_test = 1
				break
			#if re.search(r"Firmware Version*\s+Major \d{2}\. Minor \d{2}. type \d\. Build [A-Z]\d{2}\.", output):
			#if re.search(r"Firmware Version*\s+Major \d{2}\. Minor \d{2}. type \d\. Build [A-Z]\d{2}\.", output):
			#	pass_test = 1
			#	break
		else:
			pass_test = 1
			
			
		if fail_word != '':
			if fail_word in output:
				pass_test = 0
				isTestTimeOut = False
				break
				
		test_cur = time.time()
		
	console_log_print("\n################################################################\n");	
	console_log_print(" " + name + " RESULT:\n");
	console_log_print("################################################################\n");
	
	if pass_test == 1:
		console_log_print("OKOK\n");
		return 0;
	else:
		global retry_time
		retry_time = retry_time - 1
		if isTestTimeOut:
			console_log_print("TIMEOUT");
		console_log_print("NGNG\n");
		if retry_time == 0:
			return 1
		console_log_print("Retrying...");
		console_log_print("Remaining Retry: "+str(retry_time));
		return 2;  #return 2 means retry
	
	
def run_testlist():
	status = 1
	templastlogfile = 'templast.log'
	global TEMP_LAST_LOG
	TEMP_LAST_LOG.close()
	for i in range(len(test_array)):
		lastlog = ''
		global retry_time
		TEMP_LAST_LOG = open(templastlogfile, "w")
		retry_time = test_array[i].retry
		
		#print i
		console_log_print("################################################################\n");	
		console_log_print(test_array[i].test_description + " search for:  " +
		                  "\"" +test_array[i].pass_phrase + "\" in " +
		                  str(test_array[i].timeout) + " seconds.\n");
		console_log_print("################################################################\n");
		# ttyUSB
		if "ttyUSB" in test_array[i].test_path:
			while(1):
				status = execute_serial_cmd(i)
				if status != 2:
					break
			
		else:
			while(1):
				status = execute_linux_cmd(i)
				if status != 2:
					break
					
		if status == 1:		# run on error
			break
		
		TEMP_LAST_LOG.close()
		#LAST_LOG    = open(lastlogfile, "w")
		#LAST_LOG.write(lastlog)
		#LAST_LOG.close()
		
		os.rename("templast.log", "last.log")
	
	global final_result
	final_result = status
			

	
def create_sn_file():
	sn_filename = 'sn.txt'
	SN = open(sn_filename, "w");
	SN.write(serial_number);
	SN.close()
	
def initiate_logging():
	#print ("created LOG.")
	console_log_print ("#########################################################################\n");	
	console_log_print ("       Board Serial Number: " + serial_number + "                                        \n");
	console_log_print ("       Test Date and Time:  " + test_time +"                         \n");

def print_test_duration():
	#time.sleep(3)
	test_end_time = datetime.datetime.now()
	test_duration = test_end_time - test_start
	console_log_print("Test Time: " + (str(test_duration)[:7]))	
	
def console_log_print(log):
	LOG.write(log)
	#global lastlog 
	#lastlog = lastlog+log
	
	if not TEMP_LAST_LOG.closed:
		TEMP_LAST_LOG.write(log)
	print (log, end = " ")
	
def create_log_dir(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)	

def read_config():
	with open (testcfg_file, 'r') as F:
		for row in F:
			if '#' in row:
				continue
			if '=' in row:
				key = row.split("=")[0].strip()		# strip() for delete '\n' and space ...
				value = row.split("=")[1].strip()
				dic_config[key] = value

def parse_testlist(testlist_file, tmp):
	with open (testlist_file, 'r') as f:
		for row in f:
			# use $$RUNMODULE to get tests from another testlist file
			if row.startswith('$$RUNMODULE'):
				row_split = row.split(' ')
				new_testlist = row_split[1].strip()+"_testlist.txt"
				if len(row_split)>2:
					parse_testlist(new_testlist, row_split[2].strip())
				else:
					parse_testlist(new_testlist, tmp)
			
			# add test items to test_array
			elif row.startswith('"'):
				test = Test()
				row_split = row.split(',')
				for i in range(len(row_split)):
					row_split[i] = row_split[i].strip()
					# "$$ARG
					if re.search('\$\$ARG', row_split[i]):
						row_split[i] = re.sub(r'\$\$ARG[0-9]', tmp, row_split[i])
					# $MODSPROMPT2 $AURIXPROMPT1 ... get value from dic_config
					if re.search(r'\$[A-Z]*[0-9]*[A-Z]*[0-9]', row_split[i]):
						#print(row_split[i])
						key = re.search(r'\$[A-Z]*[0-9]*[A-Z]*[0-9]', row_split[i])
						key = key.group(0)
						value = dic_config[key]
						#row_split[i] = value
						row_split[i] = re.sub(r'\$[A-Z]*[0-9]*[A-Z]*[0-9]', value, row_split[i])
				
				# update test
				test.test_description = row_split[0].replace("\"","")
				tmp_path = row_split[1].replace("\"","")
				if tmp_path in dic_config:
					test.test_path = dic_config[tmp_path]
				test.command = row_split[2].replace("\"","")
				test.pass_phrase = row_split[3].replace("\"","")
				test.fail_phrase = row_split[4].replace("\"","")
				if len(row_split) > 5:
					#print(row_split[5])
					#print(row_split[0])
					test.timeout = float( row_split[5].replace("\"","") )
				if len(row_split) > 6:
					#print(row_split[6])
					test.retry = int( row_split[6].replace("\"","") )
				test_array.append(test)
			
def mv_log():
	LOG.close()
	create_log_dir('log')
	logfile = determine_log_fliename(0);
	loglocation = "./log/"+str(logfile)
	os.rename("temp.log", loglocation)
	print ("Log file location: "+loglocation)
	
def determine_log_fliename(final_result):
	res = str(datetime.datetime.now())[17:]+".txt"
	return res

def print_result():
	test_result = final_result
	if (test_result):
		console_log_print("TEST FAILED!\n")
		#console_log_print("{{N:FAIL}}\n")
		console_log_print("\n"+
		"            #######      ####     ########   ###\n"+
		"            #######     ######    ########   ###\n"+
		"            ##         ##    ##      ##      ###\n"+
		"            ##         ##    ##      ##      ###\n"+
		"            #######    ########      ##      ###\n"+
		"            #######    ########      ##      ###\n"+
		"            ##         ##    ##      ##      ###\n"+
		"            ##         ##    ##   ########   ########\n"+
		"            ##         ##    ##   ########   ########\n")  #,'bright_white on_red'
		console_log_print("\n")
	else:
		console_log_print("TEST PASSED!\n")
		#console_log_print("{{N:PASS}}\n")
		console_log_print("\n"+
		"            #######      ####      ######     ######\n"+
		"            ########    ######    ########   ########\n"+
		"            ##    ##   ##    ##   ##     #   ##     #\n"+
		"            ##    ##   ##    ##    ###        ###\n"+
		"            ########   ########     ####       ####\n"+
		"            #######    ########       ###        ###\n"+
		"            ##         ##    ##   #     ##   #     ##\n"+
		"            ##         ##    ##   ########   ########\n"+
		"            ##         ##    ##    ######     ######\n")	#,'bright_white on_green'
		console_log_print("\n")
	
def printing():
	for i in range(len(test_array)):
		print('{0} | {1} | {2} | {3} | {4} | {5} | {6} | {7}'.format(i, test_array[i].test_description, test_array[i].test_path, test_array[i].command, test_array[i].pass_phrase, test_array[i].fail_phrase, test_array[i].timeout, test_array[i].retry))
		
def printing_testcfg():
	print (dic_config)

main()
