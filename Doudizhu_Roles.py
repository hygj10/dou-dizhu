# -*- coding: utf-8 -*-
"""
Created on Thu May  4 17:40:27 2017

@author: Administrator
"""
#"3" = 3
#"4" = 4
#"5" = 5
#"6" = 6
#"7" = 7
#"8" = 8
#"9" = 9
#"10" = 10
#"J" = 11
#"Q" = 12
#"K" = 13
#"A" = 14
#"2" = 15
#"SJ" = 16
#"BJ" = 17

yourcardlist = [] 
otherscardlist = []

# cardlist need to be ordered here

def isBomb (yourcardlist):
    if len(yourcardlist)  != 4 :
        return False
    return yourcardlist == yourcardlist[-1::-1]
               

def isRocket (yourcardlist):
    return yourcardlist == [16, 17]

def isChain (yourcardlist):
    if len(yourcardlist) < 5:
        return False
    if yourcardlist[-1] > 14:
        return False
    for i in range((len(yourcardlist)) - 1):
        if yourcardlist[i] != yourcardlist[i + 1] - 1:
            return False
    return True
    

def isPair (yourcardlist):
    return len(yourcardlist) == 2 and yourcardlist[1] == yourcardlist[0]

def isSingle (yourcardlist):
    return len(yourcardlist) == 1


# Bomb will be identified as isThreeWithOne

def isThreeWithOne (yourcardlist):
    if len(yourcardlist) != 4:
        return False    
    if yourcardlist[0] == yourcardlist[1]:
        three = yourcardlist[0]
        if yourcardlist[2] == three and yourcardlist[-1] < 16:
            return True;
    elif yourcardlist[-1] == yourcardlist[-2]:
        three = yourcardlist[-1]
        if yourcardlist[-3] == three and yourcardlist[0] < 16:
            return True;
    return False


def isPairChain (yourcardlist):
    n = int(len(yourcardlist) / 2)
    if (n < 3):
        return False
    if (yourcardlist[-1] == 15):
        return False
    a = 0
    for i in range(n):
        if yourcardlist[a] != yourcardlist[a + 1]:
            return False
        else:
            a += 2            
    return True

def isAirplain (yourcardlist):
    if len(yourcardlist) != 8:
        return False;
    part1 = yourcardlist[:4]
    part2 = yourcardlist[4:]
    a = isThreeWithOne(part1)
    b = isThreeWithOne(part2)
    if (a == True and b == True):
        if (yourcardlist[4] - yourcardlist[3] == 1):
            return True
    else:
        part1 = yourcardlist[:3]
        part1.append(yourcardlist[-2])
        part2 = yourcardlist[3:6]
        part2.append(yourcardlist[-1])
        a = isThreeWithOne(part1)
        b = isThreeWithOne(part2)
        if (a == True and b == True):
            if (yourcardlist[3] - yourcardlist[2] == 1):
                return True
        else:
            part1 = yourcardlist[2:5]
            part1.append(yourcardlist[0])
            part2 = yourcardlist[5:]
            part2.append(yourcardlist[1])
            a = isThreeWithOne(part1)
            b = isThreeWithOne(part2)
            if (a == True and b == True):
                if (yourcardlist[5] - yourcardlist[4] == 1):
                    return True    
    return False;

def isFourWithTwo (yourcardlist):
    if len(yourcardlist) != 6:
        return False
    bomb = yourcardlist[:4]
    pair = yourcardlist[4:]
    if isBomb(bomb) == True and isPair(pair) == True:
        return True
    else:
        pair = yourcardlist[:2]
        bomb = yourcardlist[2:]
        if isBomb(bomb) == True and isPair(pair) == True:
            return True        
    return False

def isAplay(yourcardlist):
    return isBomb (yourcardlist) or isRocket (yourcardlist) or isChain (yourcardlist) or isPair (yourcardlist) or isSingle (yourcardlist) or isThreeWithOne (yourcardlist) or isPairChain(yourcardlist) or isAirplain (yourcardlist)
                
            
def validplay(yourcardlist, otherscardlist):
    otherssize = len(otherscardlist)
    yoursize = len(yourcardlist)
    
    #Haven't deal with bomb yet
    if otherssize != yoursize:
        return False
    size = yoursize
    
    if size == 1:
        return yourcardlist[0] > otherscardlist[0]
    
    elif size == 2:
        a = isPair(yourcardlist)
        b = isPair(otherscardlist)
        if a == True and b == True:
            return yourcardlist[0] > otherscardlist[0]
        
    elif size == 3:
        return False
    
    elif size == 4:        
        a = isBomb(yourcardlist)
        b = isBomb(otherscardlist)
        if a == True and b == True:
            return yourcardlist[0] > otherscardlist[0]
        else:
            a = isThreeWithOne(yourcardlist)
            b = isThreeWithOne(otherscardlist)
            if a == True and b == True:
                return yourcardlist[1] > otherscardlist[1]
            
    elif size == 5:
        a = isChain(yourcardlist)
        b = isChain(otherscardlist)
        if a == True and b == True:
            return yourcardlist[0] > otherscardlist[0]
        
    elif size == 6:
        a = isPairChain(yourcardlist)
        b = isPairChain(otherscardlist)
        if a == True and b == True:
            return yourcardlist[0] > otherscardlist[0]
        else:
            a = isFourWithTwo(yourcardlist)
            b = isFourWithTwo(otherscardlist)
            if a == True and b == True:
                return yourcardlist[3] > otherscardlist[3]
            else:
                a = isChain(yourcardlist)
                b = isChain(otherscardlist)
                return yourcardlist[0] > otherscardlist[0]
            
    elif size == 7:
        a = isChain(yourcardlist)
        b = isChain(otherscardlist)
        if a == True and b == True:
            return yourcardlist[0] > otherscardlist[0]
            
    elif size == 8:
        a = isPairChain(yourcardlist)
        b = isPairChain(otherscardlist)
        if a == True and b == True:
            return yourcardlist[0] > otherscardlist[0]
        else:
            a = isAirplain(yourcardlist)
            b = isAirplain(otherscardlist)
            if a == True and b == True:
                #how to deal with the airplane comparison
                return yourcardlist[2] > otherscardlist[2]
            else:
                a = isChain(yourcardlist)
                b = isChain(otherscardlist)
                return  yourcardlist[0] > otherscardlist[0]
    else:
        a = isPairChain(yourcardlist)
        b = isPairChain(otherscardlist)        
        if a == True and b == True:
            return yourcardlist[0] > otherscardlist[0]
        else:
            a = isChain(yourcardlist)
            b = isChain(otherscardlist)
            if a == True and b == True:
                return yourcardlist[0] > otherscardlist[0]     
  
    return False


l1 = [3,3,3,4,4,4,7,12]
l2 = [2,5,5,5,6,6,6,10]
l3 = [3,4,5,5,5,6,6,6]


print(validplay(l2,l1))

