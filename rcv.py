#!/Anaconda3/python
# Calculate how many possible ballot combinations 
# are created under ranked-choice voting


def rcv_combos(c: int, r: int):
	p = c - r
	if 0 > p:
		p = 0
	fact = 1
	remainder = list()
	for i in range(c, p, -1):
		fact = fact * i
		remainder.append(fact)
	remainder = remainder[:-1]
	for value in remainder:
		fact += value

	return(fact)

c = 10  # number of candidates
r = 5  # number of rank positions (1 to r)
combos = rcv_combos(c, r)
print(combos)
