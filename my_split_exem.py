def my_split(i1):
	if type(i1) is not str:
		return "Error: text only input"
	
	accum1 = 1
	accum2 = 1
	while (len(i1)-accum1) >= 0 and (len(i1)-accum2) >= 0:
		accum1 += 1
		accum2 += 1
	if (len(i1)-accum1) < 0:
		return [i1]
	elif (len(i1)-accum2) < 0:
		return [i1[0], i1[2]]
