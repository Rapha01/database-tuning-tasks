from os import mkdir, path
from db import DATA_PATH

def run():
	if path.exists(DATA_PATH):
		print('data path already exists')
		return

	mkdir(DATA_PATH)
	filepath = './'+DATA_PATH+'/data.tsv'
	with open(filepath, 'w+') as file:

		# company account first:
		file.write('0')
		file.write('\t')
		file.write('100')
		file.write('\n')

		# then the slaves
		i = 1
		while i < 101:
			file.write(str(i))
			file.write('\t')
			file.write('0\n')
			i = i + 1
		file.close()


if __name__ == "__main__":
	run()
