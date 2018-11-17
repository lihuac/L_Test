#import serial
import re
import os
import datetime
import time
import subprocess

testlist_file = 'part2a_testlist.txt'
serial_number = '1234567'
testcfg_file  = 'test.cfg'
templogfile   = 'temp.log'
directory     = 'log'
test_time     = str(datetime.datetime.now())[:19]
SERIAL_CMD    = 1
LINUX_CMD     = 0

dic_config    = {}
test_array    = []

LOG           = open(templogfile, "w")


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
	#create_log_dir(directory)
	read_config()
	#printing_testcfg()
	tmp = ''
	parse_testlist(testlist_file, tmp)
	printing()
	#create_sn_file()
	initiate_logging()
	run_testlist()
	LOG.close()
	

#	my $status = check_result($test_item[$line]{'test_description'},
#							  $test_item[$line]{'pass_phrase'}, 
#							  $test_item[$line]{'fail_phrase'}, 
#							  $test_item[$line]{'timeout'},1, \$port{$testpath});

	
def execute_linux_cmd(test_index):
	console_log_print("Linux Test for test item " + str(test_index) + "\n\n")
	return
	path = test_array[test_index].test_path
	cmd = test_array[test_index].command
	status = 1
	print "start linux command"
	if path != '':
		# change directory
		print "change directory"
	if cmd != '':
		# cmd
		cmd = 'dir'
		print "command is "+cmd
		res = ''
		res = subprocess.check_result(cmd)
		print "res is " + res
		#status = check_result(test_index, LINUX_CMD, 0)
	else:
		status = check_result(test_index, LINUX_CMD, 2)
		
	print ("linux: " + path+" " +cmd)
	
def execute_serial_cmd(test_index):
	console_log_print("Serial Test for test item " + str(test_index) + "\n\n")

def check_result(index, cmd_type, ref_port):
	name       = test_array[index].test_description
	pass_word  = test_array[index].pass_phrase
	fail_word  = test_array[index].fail_phrase
	time_out   = test_array[index].time_out
	retry_time = test_array[index].retry
	result      = 0
	res_content = ''
	output      = ''
	while(retry_time >= 0):
		start_time      = datetime.datetime.now()
		start_seconds   = time.mktime(start_time.timetuple())
		current_time    = datetime.datetime.now()
		current_seconds = time.mktime(current_time.timetuple())
		while(1):							# 
			if time_out > 0 and current_seconds-start_seconds > time_out:
				print "time over"
				console_log_print("TIMEOUT")
				break
			time.sleep(1)
			
			if cmd_type == SERIAL_CMD:		# serial port command
				print "serial"
				#_____ update res_content here
				
			elif cmd_type == LINUX_CMD:		# linux port command
				print "linux"
				#_____ update res_content here
			else:
				print "wrong cmd type"
				
			output = output + res_content
			console_log_print(res_content)
		
			if pass_word != '':
				if pass_word in output:
					result = 1
					break
			
			if fail_word != '':
				if fail_word in output:
					time_out = 0
					break
					
			current_time = datetime.datetime.now()
			current_seconds = time.mktime(current_time.timetuple())
			# Ending ...
		if result == 1:
			break
		console_log_print("NONO Retrying...");
		console_log_print("Remaining Retry: "+ retry_time +"\n\n");
		retry_time = retry_time - 1
		# Ending retry ...
	
	console_log_print("\n################################################################\n");	
	console_log_print(" " + name + " RESULT:\n");
	console_log_print("################################################################\n");
	if result == 1:
		console_log_print("OKOK\n")
		return 0
	else:
		console_log_print("NONO\n")
		return 1
	
	
def run_testlist():
	for i in range(len(test_array)):
		#print i
		console_log_print("################################################################\n");	
		console_log_print(test_array[i].test_description + " search for:  " +
		                  "\"" +test_array[i].pass_phrase + "\" in " +
		                  test_array[i].timeout + " seconds.\n");
		console_log_print("################################################################\n");
		# ttyUSB
		if "ttyUSB" in test_array[i].test_path:
			execute_serial_cmd(i)
			
		else:
			execute_linux_cmd(i)
			
def init_serial_port(test_index):
	path = test_array[test_index].test_path
	ser = serial.Serial(
		port='/dev/ttyUSB0', 
		baudrate=115200, 
		#timeout=1,
		parity=serial.PARITY_NONE,
		stopbits=serial.STOPBITS_ONE,
		bytesize=serial.EIGHTBITS,
		rtscts=False
	)
	
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
	
	
def console_log_print(log):
	LOG.write(log)
	print (log)
	
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
					if row_split[i].startswith('"$$ARG'):
						row_split[i] = re.sub(r'\$\$ARG[0-9]', tmp, row_split[i])
					# $MODSPROMPT2 $AURIXPROMPT1 ... get value from dic_config
					if re.search(r'^"\$[A-Z]*[0-9]', row_split[i]):
						key = re.search(r'\$[A-Z]*[0-9]', row_split[i])
						key = key.group(0)
						value = dic_config[key]
						row_split[i] = value
				
				# update test
				test.test_description = row_split[0].replace("\"","")
				tmp_path = row_split[1].replace("\"","")
				if tmp_path in dic_config:
					test.test_path = dic_config[tmp_path]
				test.command = row_split[2].replace("\"","")
				test.pass_phrase = row_split[3].replace("\"","")
				test.fail_phrase = row_split[4].replace("\"","")
				if len(row_split) > 5:
					test.timeout = row_split[5].replace("\"","")
				if len(row_split) > 6:
					test.retry = row_split[6].replace("\"","")
				test_array.append(test)
			
	
		
def printing():
	for i in range(len(test_array)):
		print('{0} | {1} | {2} | {3} | {4} | {5} | {6}'.format(test_array[i].test_description, test_array[i].test_path, test_array[i].command, test_array[i].pass_phrase, test_array[i].fail_phrase, test_array[i].timeout, test_array[i].retry))
		
def printing_testcfg():
	print dic_config

main()
