import os.path

count = 0

files = os.listdir(".")
for x in files:
	if os.path.isfile(x):
		with open(x) as f:
			for line in f:
				count+=1

print(count) 
