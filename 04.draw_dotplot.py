from lib.KJH_SVG.KJH_SVG import element
from lib.JobTimer.JobTimer import JobTimer
###########################################################################################
def cal_pos(pos):
    POS_RATE = 0.00002
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
class LeastSquaresMethod:
    def __init__(self):
        self.xPos_LIST = []
        self.yPos_LIST = []

    def add(self, xsPOS, xePOS, ysPOS, yePOS):
        self.xPos_LIST += [(xsPOS, xePOS)]
        self.yPos_LIST += [(ysPOS, yePOS)]

    def add_LIST(self, xPos_LIST, yPos_LIST):
        self.xPos_LIST += xPos_LIST
        self.yPos_LIST += yPos_LIST
        
    def sum_of_arithmetic_sequence(self, start, diff, length):
        return length*(2*start + (length - 1)*diff)/2
        
    def residual_sum(self, start, length):
        if start > 0:
            return self.sum_of_arithmetic_sequence(start, 2, length)
        if start + 2 * length < 0:
            return self.sum_of_arithmetic_sequence(-start, -2, length)
        else:
            return self.sum_of_arithmetic_sequence(-start, -2, -start/2) + self.sum_of_arithmetic_sequence(0, 2, length + start/2)
            
    def cal_sum_and_len(self, sPos, ePos):
        x1 = min(sPos, ePos)
        x2 = max(sPos, ePos)    
        n = x2 - x1 // 1 + 1
        sum = n * (x1 + x2) //2
        len = abs(x2 - x1) + 1
        return sum, len
        
    def get_slope_and_intercept(self):
        self.sum_x = 0
        self.len_x = 0
        self.sum_y = 0
        self.len_y = 0
        for (x1, x2), (y1, y2) in zip(self.xPos_LIST, self.yPos_LIST):
            _sum_x, _len_x = self.cal_sum_and_len(x1, x2)
            self.sum_x += _sum_x
            self.len_x += _len_x
            _sum_y, _len_y = self.cal_sum_and_len(y1, y2)
            self.sum_y += _sum_y
            self.len_y += _len_y
        self.mean_x = self.sum_x / self.len_x
        self.mean_y = self.sum_y / self.len_y
        intercept_p = self.mean_y - self.mean_x
        intercept_m = self.mean_y + self.mean_x
        residual_p = 0
        residual_m = 0
        for (x1, x2), (y1, y2) in zip(self.xPos_LIST, self.yPos_LIST):
            slope = (y2 - y1) / (x2 - x1)
            if slope == 1:
                diff_p = abs((x1 + intercept_p) - y1)
                residual_p += diff_p * (x2 - x1  + 1)
                diff_m = y1 - (intercept_m - x1)
                residual_m += self.residual_sum(diff_m, x2 - x1  + 1)
            else:
                diff_p = (x1 + intercept_p) - y1
                residual_p += self.residual_sum(diff_p, x2 - x1  + 1)
                diff_m = abs((intercept_m - x1) - y1)
                residual_m += diff_m * (x2 - x1  + 1)
        #print(residual_p/len_x)
        #print(residual_m/len_x)
        if residual_p < residual_m:
            return  1, intercept_p, min([residual_p/self.len_x, residual_m/self.len_x])/max([residual_p/self.len_x, residual_m/self.len_x])
        else:
            return -1, intercept_m, min([residual_p/self.len_x, residual_m/self.len_x])/max([residual_p/self.len_x, residual_m/self.len_x])
###########################################################################################
class DOTPLOT:
    def __init__(self, container, seqName, seqLen):
        self.lsm = LeastSquaresMethod()


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
        self.background.attr('fill', 'rgba(0,0,0,0.05)')
        self.background.attr('stroke', 'gray')
        self.background.attr('stroke-width', '1')

    def set_position(self):
        x1, x2, y1, y2 = cal_pos(self.xMIN), cal_pos(self.xMAX), cal_pos(self.yMIN), cal_pos(self.yMAX)
        height = y2 - y1
        width = x2 - x1

        slope, intercept, rate = self.lsm.get_slope_and_intercept()
        coverage = float(self.lsm.len_x) / self.seqLen

        if rate > 0.8 or coverage < 0.05:
            self.g.isVisable = False
            return

        #self.text.add('r:{0:.3f},c:{1:.3f}'.format(rate, coverage))

        x = cal_pos(intercept)
        y = 0

        if slope == 1:
            self.g.attr('transform', 'translate({0},{1}) '.format(x, y))
            self.text.attr('x', x1 + 4)
            self.text.attr('y', y1 -  2)
        else:
            self.g.attr('transform', 'translate({0},{1}) scale(-1, 1) '.format(x, y))
            self.text.attr('x', x1 + 4 - width)
            self.text.attr('y', y1 - 2)
            self.text.attr('transform', 'scale(-1, 1)')

        return self

    def add_dot(self, xsPOS, xePOS, ysPOS, yePOS):
        self.lsm.add(xsPOS, xePOS, ysPOS, yePOS)

        line = element('line', self.g)

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
infile = 'query_100.exact_pos.dups'
jobTimer = JobTimer()

xFAR = FAIDX_READER('query.fa.fai')
yFAR = FAIDX_READER('ref/ref.fa.fai')

image_DICT = {}

fin = open(infile)
lineN = sum(1 for _ in fin)
fin.close()

jobTimer.reset()
fin = open(infile)

for lineIDX, line in enumerate(fin):
    if (lineIDX)%int(lineN / 100) == 0:
        jobTimer.check()
        percentage = float(lineIDX+1)/lineN
        print("Read File... [{0:6.2f}%] remainTime: {1}".format(percentage*100, jobTimer.remainTime(percentage)))

    xNAME, yNAME, xLen, rLen, xsPOS, xePOS, ysPOS, yePOS = line.rstrip('\n').split('\t')

    xLen = int(xLen)
    #if xLen < 500: continue

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