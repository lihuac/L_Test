
import re

testlist_file = 'part2a_testlist.txt'
testcfg_file  = 'test.cfg'

dic_config = {}
test_array = []

class Test:
	test_description = ""
	test_path = ""
	command = ""
	pass_phrase = ""
	fail_phrase = ""
	timeout = 0
	retry = 0

# Test MAIN	
def main():
	read_config()
	#printing_testcfg()
	
	parse_testlist(testlist_file)
	printing()
	
	
def run_testlist():
	print ("running")
	
def read_config():
	with open (testcfg_file, 'r') as F:
		for row in F:
			if '=' in row:
				key = row.split("=")[0].strip()		# strip() for delete '\n' and space ...
				value = row.split("=")[1].strip()
				dic_config[key] = value

def parse_testlist(testlist_file):
	with open (testlist_file, 'r') as f:
		for row in f:
			# use $$RUNMODULE to get tests from another testlist file
			if row.startswith('$$RUNMODULE'):
				row_split = row.split(' ')
				new_testlist = row_split[1].strip()+"_testlist.txt"
				parse_testlist(new_testlist)
			
			# add test items to test_array
			elif row.startswith('"'):
				test = Test()
				row_split = row.split(',')
				for i in range(len(row_split)):
					row_split[i] = row_split[i].strip()
					# "$$ARG
					if row_split[i].startswith('"$$ARG'):
						row_split[i] = re.sub(r'\$\$ARG[0-9]', '', row_split[i])
					# $MODSPROMPT2 $AURIXPROMPT1 ... get value from dic_config
					if re.search(r'^"\$[A-Z]*[0-9]', row_split[i]):
						key = re.search(r'\$[A-Z]*[0-9]', row_split[i])
						key = key.group(0)
						value = dic_config[key]
						row_split[i] = value
						print row_split[i]
				
				# update test
				test.test_description = row_split[0]
				test.test_path = row_split[1]
				test.command = row_split[2]
				test.pass_phrase = row_split[3]
				test.fail_phrase = row_split[4]
				if len(row_split) > 5:
					test.timeout = row_split[5]
				if len(row_split) > 6:
					test.retry = row_split[6]
				test_array.append(test)
			
	
		
def printing():
	for i in range(len(test_array)):
		print('{0} | {1} | {2} | {3} | {4} | {5} | {6}'.format(test_array[i].test_description, test_array[i].test_path, test_array[i].command, test_array[i].pass_phrase, test_array[i].fail_phrase, test_array[i].timeout, test_array[i].retry))
		
def printing_testcfg():
	print dic_config

main()
