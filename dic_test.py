
file = 'test.cfg'

dic_config = {}
test_array = []

class Testlist:
	test_description = "des"
	test_path = ""
	command = ""
	pass_phrase = ""
	fail_phrase = ""
	timeout = ""
	retry = ""

def read_config():
	with open (file, 'r') as F:
		for row in F:
			if '=' in row:
				key = row.split("=")[0]
				value = row.split("=")[1]
				dic_config[key] = value

	print (dic_config)


	
def parse_testlist():
	for i in range(10):
		test = Testlist()
		test.test_description = i
		test.test_path = str(i)+"'s path"
		test_array.append(test)

		
def printing():
	for i in range(10):
		print (test_array[i].test_description)


# calling functions from here	

read_config()
		
parse_testlist()

printing()
	    
    