#的撒解耦is到ij
#grammarList=input('请输入文法，其格式要符合要求').split('\n')
grammarList='''
S->（L）|a
L->SK
K->，SK|ε
'''.split('\n')
while '' in grammarList:
    grammarList.remove('')
nonTerminals=[]
terminals=[]
nonAbles=[]
firstSet={}
followSet={}
formatedGrammarList={}
dirty=False #检测集合是否变动的布尔值
debug=True #是否开启调试模式，每一步集合变动均打印在终端

def init():
    #初始化非终结符和终结符，以及格式化文法
    for i in grammarList:
        if i[0] not in nonTerminals:
            nonTerminals.append(i[0])
    for i in grammarList: 
        for char in i:
            #print(char)
            
            if char.isupper() and char not in nonTerminals:
                nonTerminals.append(char)
                print('居然有不在第一位的非终结符！它就是{}'.format(char))
            if not char.isupper() and char!='-' and char!='>' and char!='|' and char!='ε':
                #print(char)
                terminals.append(char)
            if char=='ε':
                #将该非终结符号加入nonAble
                nonAbles.append(i[0])
        tempList=i.split('->')#临时列表，第一个元素是每行产生式的第一个非终结符号
        if tempList[0] not in formatedGrammarList:
            formatedGrammarList[tempList[0]]=tempList[1].split('|')
        else:
            for expression in tempList[1].split('|'):
                if expression not in formatedGrammarList[tempList[0]]:
                    formatedGrammarList[tempList[0]].append(expression)

    #初始化FirstSet
    for i in nonTerminals:
        if i in nonAbles:
            firstSet[i]=['ε']
        else:
            firstSet[i]=[]
    for i in terminals:
        firstSet[i]=[i]
    firstSet['ε']=['ε']#特殊定义，为方便编码

    #初始化FollowSet
    followSet[nonTerminals[0]]=['$']
    for nonTerminal in nonTerminals:
        if nonTerminal not in followSet:
            followSet[nonTerminal]=[]

#计算FirstSet的函数
def computeFirstSet():
    while True:
        dirty=False
        for expressionHead in formatedGrammarList:
            for expressionRight in formatedGrammarList[expressionHead]:
                #从前往后扫描字符，如果遇到可空的非终结符号就把这个符号的FirstSet的元素加入到当前产生式头部的非终结符号的FirstSet中
                for char in expressionRight:
                    if char in nonAbles:
                        for i in firstSet[char]:
                            if i not in firstSet[expressionHead]:
                                firstSet[expressionHead].append(i)
                                dirty=True #只有更新才置True
                    else: #遇到了不可空的符号，那就把这个符号的FirstSet的元素并入到当前产生式头部的非终结符号的FirstSet中，并停止继续扫描，注意，我定义ε也不属于不可空的非终结符号，所以如果扫描到ε直接加入FirstSet
                        for i in firstSet[char]:
                            if i not in firstSet[expressionHead]:
                                firstSet[expressionHead].append(i)
                                dirty=True #只有更新才置True
                        break #退出扫描循环
                else: #如果全部的字符都是可空的，那就把ε加入到当前产生式头部的非终结符号的FirstSet中
                    if 'ε' not in firstSet[expressionHead]:
                        firstSet[expressionHead].append('ε')
                        dirty=True #只有更新才置True
        if dirty==False: #如果该轮循环FirstSet集合未更新
            break

#计算串的First的函数，用于计算FollowSet，只能在FirstSet已经计算好的时候使用，否则无效
def first(alpha):
    #computeFirstSet()
    returnFirstSet=[]
    for char in alpha:
        if char in nonAbles:
            for i in firstSet[char]:
                if (i!='ε') and (i not in returnFirstSet): returnFirstSet.append(i)
        else:
            for i in firstSet[char]:
                returnFirstSet.append(i)
            break
    else:
        returnFirstSet.append('ε')
    return returnFirstSet

#计算FollowSet的函数
def computeFollowSet():
    while True:
        dirty=False
        for expressionHead in formatedGrammarList:
            for expressionRight in formatedGrammarList[expressionHead]:
                #逐个从左往右扫描产生式右部，扫描到非终结符就处理
                for i in range(expressionRight.__len__()):
                    if expressionRight[i] in nonTerminals:
                        #对于A->αBβ的产生式，要将β的FirstSet中的所有不是ε的元素加入到B的FollowSet中
                        if i!=expressionRight.__len__()-1:
                            for char in first(expressionRight[i+1:]):
                                if char not in followSet[expressionRight[i]] and char!='ε':
                                    followSet[expressionRight[i]].append(char)
                                    dirty=True #只有更新才置True
                        #对于A->αBβ的产生式，如果β的FirstSet中包含ε，或者产生式是A->αB，则要将A的FollowSet中的全部元素加入到B的FollowSet中
                        if i==expressionRight.__len__()-1 or 'ε' in first(expressionRight[i+1:]):
                            for char in followSet[expressionHead]:
                                if char not in followSet[expressionRight[i]]:
                                    followSet[expressionRight[i]].append(char)
                                    dirty=True #只有更新才置True           
        if dirty==False:
            break                    

#调试模式下计算FirstSet的函数
def debugFirstSet():
    round=1 #输出轮次
    print('\n【正在计算FirstSet】')
    while True:
        print('-----------第{}轮次-----------'.format(round))
        dirty=False
        for expressionHead in formatedGrammarList:
            for expressionRight in formatedGrammarList[expressionHead]:
                #从前往后扫描字符，如果遇到可空的非终结符号就把这个符号的FirstSet的元素加入到当前产生式头部的非终结符号的FirstSet中
                for char in expressionRight:
                    if char in nonAbles:
                        for i in firstSet[char]:
                            if i not in firstSet[expressionHead]:
                                firstSet[expressionHead].append(i)
                                dirty=True #只有更新才置True
                                print('产生式【{}->{}】中符号{}是可空非终结符号，且该符号前面串为可空串，故将{}的FirstSet中的所有符号加入{}的FirstSet，当前加入的符号为{}'.format(expressionHead,expressionRight,char,char,expressionHead,i))
                    else: #遇到了不可空的符号，那就把这个符号的FirstSet的元素并入到当前产生式头部的非终结符号的FirstSet中，并停止继续扫描，注意，我定义ε也不属于不可空的非终结符号，所以如果扫描到ε直接加入FirstSet
                        for i in firstSet[char]:
                            if i not in firstSet[expressionHead]:
                                firstSet[expressionHead].append(i)
                                dirty=True #只有更新才置True
                                print('产生式【{}->{}】中符号{}是不可空非终结符号，且该符号前面串为可空串，故将{}的FirstSet中的所有符号加入{}的FirstSet并停止扫描，当前加入的符号为{}'.format(expressionHead,expressionRight,char,char,expressionHead,i))
                        break #退出扫描循环
                else: #如果全部的字符都是可空的，那就把ε加入到当前产生式头部的非终结符号的FirstSet中
                    if 'ε' not in firstSet[expressionHead]:
                        firstSet[expressionHead].append('ε')
                        dirty=True #只有更新才置True
                        print('产生式【{}->{}】中所有符号均可空，所以将ε加入{}的FirstSet'.format(expressionHead,expressionRight,expressionHead))
        round+=1
        if dirty==False: #如果该轮循环FirstSet集合未更新
            print('本轮次中集合未发生改变，算法停止')
            break

#调试模式下计算串的First的函数，用于计算FollowSet，只能在FirstSet已经计算好的时候使用，否则无效
def debugFirst(alpha):
    #computeFirstSet()
    returnFirstSet=[]
    for char in alpha:
        if char in nonAbles:
            for i in firstSet[char]:
                if (i!='ε') and (i not in returnFirstSet): returnFirstSet.append(i)
        else:
            for i in firstSet[char]:
                returnFirstSet.append(i)
            break
    else:
        returnFirstSet.append('ε')
    return returnFirstSet

#调试模式下计算FollowSet的函数
def debugFollowSet():
    round=1 #输出轮次
    print('\n【正在计算FollowSet】')
    while True:
        print('-----------第{}轮次-----------'.format(round))
        dirty=False
        for expressionHead in formatedGrammarList:
            for expressionRight in formatedGrammarList[expressionHead]:
                #逐个从左往右扫描产生式右部，扫描到非终结符就处理
                for i in range(expressionRight.__len__()):
                    if expressionRight[i] in nonTerminals:
                        #对于A->αBβ的产生式，要将β的FirstSet中的所有不是ε的元素加入到B的FollowSet中
                        if i!=expressionRight.__len__()-1:
                            for char in debugFirst(expressionRight[i+1:]):
                                if char not in followSet[expressionRight[i]] and char!='ε':
                                    followSet[expressionRight[i]].append(char)
                                    dirty=True #只有更新才置True
                                    print('产生式【{}->{}】符号{}后跟着的串{}的FirstSet要全部加入（除了ε）到该符号的FollowSet中，当前加入的符号为{}'.format(expressionHead,expressionRight,expressionRight[i],expressionRight[i+1:],char))
                        #对于A->αBβ的产生式，如果β的FirstSet中包含ε，或者产生式是A->αB，则要将A的FollowSet中的全部元素加入到B的FollowSet中
                        if i==expressionRight.__len__()-1 or 'ε' in debugFirst(expressionRight[i+1:]):
                            for char in followSet[expressionHead]:
                                if char not in followSet[expressionRight[i]]:
                                    followSet[expressionRight[i]].append(char)
                                    dirty=True #只有更新才置True        
                                    print('产生式【{}->{}】符号{}后跟着的串{}的FirstSet中包含ε，所以要将{}的FollowSet全部加入到该符号的FollowSet中，当前加入的符号为{}'.format(expressionHead,expressionRight,expressionRight[i],expressionRight[i+1:],expressionHead,char))   
        round+=1
        if dirty==False:
            print('本轮次中集合未发生改变，算法停止')
            break                    

def printFirstSet():
    print('----------------------\nFirstSet:')
    for key in firstSet:
        if key in nonTerminals:
            print(key,end=': ')
            for i in firstSet[key]:
                print(i,end='\t')
            print()
    print('----------------------')

def printFollowSet():
    print('----------------------\nFollowSet:')
    for key in followSet:
        if key in nonTerminals:
            print(key,end=': ')
            for i in followSet[key]:
                print(i,end='\t')
            print()
    print('----------------------')

def normalMode():
    init()
    computeFirstSet()
    computeFollowSet()
    printFirstSet()
    printFollowSet()

def debugMode():
    init()
    debugFirstSet()
    debugFollowSet()
    printFirstSet()
    printFollowSet()

if __name__=='__main__':
    if debug:
        debugMode()
    else:
        normalMode()