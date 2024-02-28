#!/usr/bin/python
#This script is written by Jingwei Xu, ETH Zurich

try:
        from optparse import OptionParser, OptionGroup
except:
        from optik import OptionParser
import sys, os, glob, time, math, commands, stat, shutil, random

#try to automatically define the search range based on the ptcls coordinates (find the overlap area among different coordinate files)

def main():
	usage = """python tomo_sampling.py [coordinate_file] --options
	For example:
	python tomo_sampling.py test.txt --search_rangex 450:550 --search_rangey 550:650 --search_rangez 150:250 --seed_num 2 --angpix 2.678
	"""
	parser = OptionParser(usage=usage)
	parser.add_option("--seed_num", dest="seed_num", type="int", help="The number of seeds to be generated for the processing. The default is 5.", default=5)
	parser.add_option("--boxsize_series", dest="boxsize_series", type="string", help="The serial boxsize (radius) for the processing. Each boxsize is seperated based on ':'. The default is '20:40:60'.", default="20:40:60")
	parser.add_option("--tomo_x", dest="tomo_x", type="int", help="The dimension X of the tomogram at binning=4 (K3 camera). The default is 1024.", default=1024)
	parser.add_option("--tomo_y", dest="tomo_y", type="int", help="The dimension Y of the tomogram at binning=4 (K3 camera). The default is 1440.", default=1440)
	parser.add_option("--tomo_z", dest="tomo_z", type="int", help="The dimension Z of the tomogram. The default is 300.", default=300)
	parser.add_option("--search_rangex", dest="search_rangex", type="string", help="The search range of dimension X. The start and end of range is seperated based on ':'. The default is '1:1024'.", default="1:1024")
	parser.add_option("--search_rangey", dest="search_rangey", type="string", help="The search range of dimension Y. The start and end of range is seperated based on ';'. The default is '1:1440'.", default="1:1440")
	parser.add_option("--search_rangez", dest="search_rangez", type="string", help="The search range of dimension Z. The start and end of range is seperated based on ';'. The default is '1:300'.", default="1:300")
	parser.add_option("--angpix", dest="angpix", type="float", help="The pixel size of the tomogram. The default is 1.0.", default=1.0)
	parser.add_option("--print_result", dest="print_result", action="store_true", help="To print out the result, including sampling center, boxsize, and the number of ptcls in the sub-volume. The default is False.", default=False)
	parser.add_option("--print_points", dest="print_points", action="store_true", help="To print out the points in the box, just for debugging. The default is False.", default=False)
	(options, args) = parser.parse_args()
	
	if len(args) < 1:
		print "ERROR: please provide the input coordinate file for processing. Exit!"
		print usage
		sys.exit(-1)
		
	cord_file = args[0]
	if not(os.path.exists(cord_file)):
		print "ERROR: the input coordinate file does not exist! Please check it. Exit!"
		print usage
		sys.exit(-1)
		
	cord_txt = open(cord_file, "r").readlines()
	
#Assuming that each line contains cord_X (#1), cord_Y (#2), cord_Z (#3)
	cord_lst = []
	for i in cord_txt:
		cord_X = float(i.split()[1])
		cord_Y = float(i.split()[2])
		cord_Z = float(i.split()[3])
		cord_info = (cord_X, cord_Y, cord_Z)
		cord_lst.append(cord_info)
	
	print "There are %d coordinates in the file %s."%(len(cord_lst), cord_file)
	
	tomo_x = options.tomo_x
	tomo_y = options.tomo_y
	tomo_z = options.tomo_z
	angpix = options.angpix
	seed_num = options.seed_num

	boxsize_lst = []
	for i in options.boxsize_series.split(':'):
		boxsize_lst.append(int(i))

	start_x = int(options.search_rangex.split(':')[0])
	end_x = int(options.search_rangex.split(':')[-1])
	start_y = int(options.search_rangey.split(':')[0])
	end_y = int(options.search_rangey.split(':')[-1])
	start_z = int(options.search_rangez.split(':')[0])
	end_z = int(options.search_rangez.split(':')[-1])
	
	x_lst = random.sample(range(start_x, end_x), seed_num)
	y_lst = random.sample(range(start_y, end_y), seed_num)
	z_lst = random.sample(range(start_z, end_z), seed_num)
	
	seed_lst = []
	for i in range(seed_num):
		seed_cord = (x_lst[i], y_lst[i], z_lst[i])
		seed_lst.append(seed_cord)

#layer 1: different seed (or center);
#layer 2: different boxsize
	sample_lst = []
	for seed in seed_lst:
		sample_seed_lst = []
		for boxsize in boxsize_lst:
			sample_boxsize_lst = [(seed, boxsize * 2)]
			seed_x_min = seed[0] - boxsize
			seed_x_max = seed[0] + boxsize
			seed_y_min = seed[1] - boxsize
			seed_y_max = seed[1] + boxsize				
			seed_z_min = seed[2] - boxsize
			seed_z_max = seed[2] + boxsize
			
			for cord in cord_lst:
				x, y, z = cord[:]
				if x > seed_x_min and x < seed_x_max:
					if y > seed_y_min and y < seed_y_max:
						if z > seed_z_min and z < seed_z_max:
#							print cord
#							print seed_x_min, seed_x_max, seed_y_min, seed_y_max, seed_z_min, seed_z_max
							sample_boxsize_lst.append(cord)
			sample_seed_lst.append(sample_boxsize_lst)						
		sample_lst.append(sample_seed_lst)
#	print sample_lst
	
	for seed in sample_lst:
		for i in seed:
			seed_cord, boxsize = i[0][:]
			num_ptcl = len(i) - 1
			dimension = (boxsize * angpix) ** 3
			print "There are %d particles found in %.2f Angstrom**3 sub-volume."%(num_ptcl, dimension)
			
			if options.print_result:
				print seed_cord, boxsize, num_ptcl

			if options.print_points:
				print i[1:]
	

if __name__ == "__main__":
        main()

	
