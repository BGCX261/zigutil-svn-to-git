import sys

def countAlpha(cell_km, cell_actual, input_value): 
    return (2 * cell_km) / (input_value * cell_actual)

if __name__ == '__main__':
	if len(sys.argv) == 4: 
		print 'Alpha: ' + str(countAlpha(float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])))
	else: 
		print 'ERROR: 3 parameters needed, ' + str(len(sys.argv) - 1) + ' provided. Try again.'