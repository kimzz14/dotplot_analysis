fin = open('query_100.exact_pos')

for line in fin:
    xNAME, yNAME, xLen, rLen, xsPOS, xePOS, ysPOS, yePOS = line.rstrip('\n').split('\t')
    xLen = int(xLen)
    if xLen > 1000:
        print(line.rstrip('\n'))
fin.close()