
file = 'test.cfg'

dic_config = {}
test_array = []

class Test:
	test_description = "des"
	test_path = ""
	command = ""
	pass_phrase = ""
	fail_phrase = ""
	timeout = 0
	retry = 0

def read_config():
	with open (file, 'r') as F:
		for row in F:
			if '=' in row:
				key = row.split("=")[0]
				value = row.split("=")[1]
				dic_config[key] = value

	print (dic_config)

	
def parse_testlist(testlist_file):
	
	with open (testlist_file, 'r') as f:
		for row in f:
			if row.startswith('"'):
				test = Test()
				row_split = row.split(',')
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
		print('{0} , {1} , {2} , {3} , {4} , {5} , {6}'.format(test_array[i].test_description, test_array[i].test_path, test_array[i].command, test_array[i].pass_phrase, test_array[i].fail_phrase, test_array[i].timeout, test_array[i].retry))
		


# calling functions from here	

#read_config()
		
parse_testlist('part2b_testlist.txt')

printing()
	    
    