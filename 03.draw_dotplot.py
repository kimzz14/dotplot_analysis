from lib.KJH_SVG.KJH_SVG import element
from lib.JobTimer.JobTimer import JobTimer
###########################################################################################
def cal_pos(pos):
    POS_RATE = 0.0001
    return pos * POS_RATE
###########################################################################################
def cal_sum_and_len(x1, x2):
    n = x2 - x1 // 1 + 1
    sum = n * (x1 + x2) //2
    len = abs(x2 - x1) + 1
    return sum, len
###########################################################################################
class FAIDX_READER:
    def __init__(self, fileName):
        self.fileName = fileName
        self.seqLen_DICT = {}

        fin = open(self.fileName)
        for line in fin:
            seqName, seqLen = line.rstrip('\n').split('\t')[0:2]
            self.seqLen_DICT[seqName] = int(seqLen)
        fin.close()
    
    def get(self, seqName):
        return self.seqLen_DICT[seqName]
###########################################################################################
class DOTPLOT:
    def __init__(self, container, seqName, seqLen):
        self.seqName = seqName
        self.seqLen = seqLen

        self.g = element('g', container)
        self.text = element('text', self.g)
        self.text.add(self.seqName)
        self.text.attr('font-size', 10)

        self.background = element('rect', self.g)
        
        self.xMIN, self.xMAX, self.yMIN, self.yMAX = 1000000000, -1, 1000000000, -1
        self.xMIN, self.xMAX = 1, self.seqLen

        self.xSum, self.xLen, self.ySum, self.yLen = 0, 0, 0, 0

    def set_background(self):
        x1, x2, y1, y2 = cal_pos(self.xMIN), cal_pos(self.xMAX), cal_pos(self.yMIN), cal_pos(self.yMAX)
        height = y2 - y1
        width = x2 - x1

        self.background.attr('x', x1)
        self.background.attr('y', y1)
        self.background.attr('height', height)
        self.background.attr('width', width)
        self.background.attr('fill', 'rgba(255,255,255,0)')
        self.background.attr('stroke', 'gray')
        self.background.attr('stroke-width', '1')

    def set_position(self):
        x1, x2, y1, y2 = cal_pos(self.xMIN), cal_pos(self.xMAX), cal_pos(self.yMIN), cal_pos(self.yMAX)
        height = y2 - y1
        width = x2 - x1

        xMean = self.xSum/self.xLen
        yMean = self.ySum/self.yLen

        intercept = abs(yMean) - abs(xMean)

        if self.xLen < 50000: 
            self.g.attr('transform', 'translate({0},{1}) '.format(10000, 10000))
            return

        x = cal_pos(intercept)
        y = 0

        if yMean > 0:
            self.g.attr('transform', 'translate({0},{1}) '.format(x, y))
            self.text.attr('x', x1 + 10 + width)
            self.text.attr('y', y1 + 2)
        else:
            self.g.attr('transform', 'translate({0},{1}) scale(-1, 1) translate({2},{3})'.format(x, y, -width, 0))
            self.text.attr('x', x1 + 10)
            self.text.attr('y', y1 + 2)
            self.text.attr('transform', 'scale(-1, 1)')

        return self

    def add_dot(self, xsPOS, xePOS, ysPOS, yePOS):
        line = element('line', self.g)

        xSum, xLen = cal_sum_and_len(xsPOS, xePOS)
        self.xSum += xSum
        self.xLen += xLen

        ySum, yLen = cal_sum_and_len(ysPOS, yePOS)
        self.ySum += ySum
        self.yLen += yLen


        x1, x2, y1, y2 = cal_pos(xsPOS), cal_pos(xePOS), cal_pos(ysPOS), cal_pos(yePOS)

        #self.xMIN, self.xMAX = min(self.xMIN, xsPOS, xePOS), max(self.xMAX, xsPOS, xePOS)
        self.yMIN, self.yMAX = min(self.yMIN, ysPOS, yePOS), max(self.yMAX, ysPOS, yePOS)
        
        line.attr('x1', x1)
        line.attr('x2', x2)
        line.attr('y1', y1)
        line.attr('y2', y2)
        line.attr('stroke', 'red')
        line.attr('stroke-width', '1')
###########################################################################################
class IMAGE:
    def __init__(self, seqName, seqLen):
        margin = 100

        self.seqName = seqName
        self.seqLen = seqLen
        self.html = element('html', None)
        self.svg = element('svg', self.html)
        self.svg.attr('viewBox', '0 0 {0} {1}'.format(cal_pos(self.seqLen) + margin * 2, cal_pos(self.seqLen) + margin * 2))
        self.svg.attr('height', cal_pos(self.seqLen) + margin * 2)
        self.svg.attr('width', cal_pos(self.seqLen) + margin * 2)
        self.svg.style('background', 'white')
        self.g = element('g', self.svg)
        self.g.attr('transform', 'translate({0},{1}) '.format(margin, margin))
        self.set_ruler()

        self.dotplot_DICT = {}
    
    def set_ruler(self):
        ref_ruler = element('rect', self.g)
        ref_ruler.attr('x', -2)
        ref_ruler.attr('y', 0)
        ref_ruler.attr('height', cal_pos(self.seqLen))
        ref_ruler.attr('width', 1)
        ref_ruler.attr('fill', 'black')
        query_ruler = element('rect', self.g)
        query_ruler.attr('x', 0)
        query_ruler.attr('y', cal_pos(self.seqLen))
        query_ruler.attr('height', 1)
        query_ruler.attr('width', cal_pos(self.seqLen))
        query_ruler.attr('fill', 'black')

    def add(self, seqName, seqLen):
        self.dotplot_DICT[seqName] = DOTPLOT(self.g, seqName, seqLen)

    def get(self, seqName):
        return self.dotplot_DICT[seqName]
###########################################################################################
jobTimer = JobTimer()

xFAR = FAIDX_READER('query.fa.fai')
yFAR = FAIDX_READER('ref/ref.fa.fai')

image_DICT = {}

fin = open('query_100.exact_pos')
lineN = sum(1 for _ in fin)
fin.close()

jobTimer.reset()
fin = open('query_100.exact_pos')
for lineIDX, line in enumerate(fin):
    if (lineIDX)%int(lineN / 100) == 0:
        jobTimer.check()
        percentage = float(lineIDX+1)/lineN
        print("Read File... [{0:6.2f}%] remainTime: {1}".format(percentage*100, jobTimer.remainTime(percentage)))

    xNAME, yNAME, xLen, rLen, xsPOS, xePOS, ysPOS, yePOS = line.rstrip('\n').split('\t')

    xLen = int(xLen)
    if xLen < 1000: continue

    if not yNAME in image_DICT: image_DICT[yNAME] = IMAGE(yNAME, yFAR.get(yNAME))
    if not xNAME in image_DICT[yNAME].dotplot_DICT: image_DICT[yNAME].add(xNAME, xFAR.get(xNAME))

    xsPOS,  xePOS, ysPOS, yePOS = int(xsPOS), int(xePOS), abs(int(ysPOS)), abs(int(yePOS))

    #print(xLen, xsPOS,  xePOS, ysPOS, yePOS)

    image_DICT[yNAME].get(xNAME).add_dot(xsPOS,  xePOS, ysPOS, yePOS)

jobTimer.check()
percentage = 1.0
print("Read File... [{0:6.2f}%] remainTime: {1}".format(percentage*100, jobTimer.remainTime(percentage)))

for yNAME, image in image_DICT.items():
    for xNAME, dotplot in image.dotplot_DICT.items():
        dotplot.set_background()
        dotplot.set_position()

    fout = open('dotplot/{0}.html'.format(yNAME), 'w')
    fout.write(str(image.html))
    fout.close()
###########################################################################################