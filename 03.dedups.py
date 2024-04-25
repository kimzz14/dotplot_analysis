fin = open('query_100.exact_pos')

pos_DICT = {}
for lineIDX, line in enumerate(fin):
    xNAME, yNAME, xLen, rLen, xsPOS, xePOS, ysPOS, yePOS = line.rstrip('\n').split('\t')
    xLen, rLen, xsPOS, xePOS, ysPOS, yePOS = map(int, [xLen, rLen, xsPOS, xePOS, ysPOS, yePOS])

    #if xLen < 300: continue

    if not xNAME in pos_DICT: pos_DICT[xNAME] = {}

    key = (xsPOS, xePOS, xLen)

    if not key in pos_DICT[xNAME]: pos_DICT[xNAME][key] = []

    pos_DICT[xNAME][key] += [line]
fin.close()

fout = open('query_100.exact_pos.dups', 'w')
for xNAME in sorted(pos_DICT.keys()):
    for key in sorted(pos_DICT[xNAME].keys()):
        line_LIST = pos_DICT[xNAME][key]

        if len(line_LIST) == 1:
            for line in line_LIST:
                fout.write(line)
fout.close()