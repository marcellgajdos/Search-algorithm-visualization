import tkinter as tk
from tkinter import ttk, filedialog #combobox miatt kell
import random 
from datetime import datetime
import time
import os

#alapveto valtozok inicializalasa
loopModifier=3
cellSize=50
size=10
walls=[] #ebbe tarolodnak a falak. 2D matrix, mely minden cellahoz a specifikacio szerint rendeli a falait
visual=[] #ebbe tarolodnak a vizualizacio cellai
#statisztikakat tarolo listak
statDF=[]
statBF=[]
statDFID=[]
statAstar=[]
statIDAstar=[]

class Node:
    def __init__(self,x,y,parent,xd=0,yd=0): # cellak tarolasara valo osztaly, az alapertelmezett celertekek miatt megfelel az osszes algorimtus node-janak tarolasara
        self.x=x
        self.y=y
        self.parent=parent
        if parent==0: # ha nincs szuloje
            self.level=0 #szintje 0
        else: #ha van szuloje
            self.level=parent.level+1 #szintje szulo szintje + 1
        g=abs(self.x-xd)+abs(self.y-yd) # heurisztikus fuggvenyt szamolunk, Manhattan tavolsaggal
        self.func=self.level+g
        
    def __str__(self): #kiiratas overload
        return f"({self.x},{self.y}) - {int(self.level)} - {self.func}"

    def __eq__(self, other): #egyenloseg overload
        return isinstance(other, Node) and self.x == other.x and self.y==other.y
    
    def __hash__(self): #hash overload listaban kereseshez
        return hash((self.x,self.y))
    
def genD1st(size):
    global walls
    maze = [[1 for _ in range(size)] for _ in range(size)] #cellak 2D matrixa, egyelore mind 1, amit bejartunk 0-ra billentjuk
    walls = [[[1,1,1,1] for _ in range(size)] for _ in range(size)] #falak toltese, ezekbol veszunk majd el

    stack = [((random.randint(0,size-1),random.randint(0,size-1)))] #stack-be taroljuk a bejart utat, viszalepeskor popoljuk a cellakat
    while stack:
        x, y = stack[-1] 
        neighbors = getPossible(x, y, maze, size) #elkerjuk a be nem jart szomszedokat

        if neighbors: #ha van be nem jart szomszed
            nx, ny = random.choice(neighbors) #random szomszed valasztasa a be nem jartak kozul

            maze[x][y] = 0 #adott cella bejart
            maze[nx][ny] = 0 #szomszedja is bejart
            updateWalls(nx, ny,x,y) #frissitjuk a falakat tartalmazo matrixot, hogy a ketto kozott ne legyen
            modifyCell(nx,ny,walls[nx][ny],'#777777',True) #grafika update
            modifyCell(x,y,walls[x][y],'#777777',True) #grafika update

            stack.append((nx, ny)) #stackbe pusholjuk a szomszedot, lekozelebb ebbol indulunk tovabb

        else: #ha nincs be nem jart szomszed, vissza kell lepni
            stack.pop() #popoljuk a cellat, ami a stack tetejen van

    modifyCell(0,0,walls[0][0],'green',True) #kezdo cella zoldre grafika 
    modifyCell(int(size/2),int(size/2),walls[int(size/2)][int(size/2)],'red',True) #cel cella pirosra grafika
    canvas.update() #megjlenitunk

def genPrim(size):
    global walls
    maze = [[1 for _ in range(size)] for _ in range(size)] #cellak 2D matrixa, egyelore mind 1, amit bejartunk 0-ra billentjuk
    walls = [[[1,1,1,1] for _ in range(size)] for _ in range(size)] #falak toltese, ezekbol veszunk majd el

    possible=set() #set-be taroljuk a lehetseges kiterjesztehto cellakat
    possible.add((random.randint(0,size-1),random.randint(0,size-1))) #betaroljuk az elso cellat manualisan
    while possible:
        poslis=list(possible) #konvertaljuk a setet listaba, hogy tudjunk random valasztani
        x, y = random.choice(poslis) #random valasztunk kiterjesztendo cellat
        
        neighbors = getPossible(x, y, maze, size) #kiterjesztendo cella szomszedait vizsgaljuk
        if neighbors: #ha van szomszed
            nx, ny = random.choice(neighbors) #valasztunk egyet random
            neighbors = getPossible(nx, ny, maze, size) #megnezzuk annak a szomszedait
            possible.add((nx,ny)) #hozzaadunk egy random szomszedot a kiterjeszthetokhoz
            maze[nx][ny] = 0 #jelezzuk a szomszed foglaltsagat
            updateWalls(nx, ny,x,y) #falakat frissitjuk
            modifyCell(x,y,walls[x][y],'#777777',True) #az eredeti cellat szinezzuk
        else: #ha nincs szomszed
            modifyCell(x,y,walls[x][y],'#777777',True) #az eredeti cellat szinezzuk
            possible.remove((x,y)) #mivel nincs tobb szabad szomszed, kivesszuk a lehetseges listarol

    modifyCell(0,0,walls[0][0],'green',True) #kezdo cella zoldre grafika 
    modifyCell(int(size/2),int(size/2),walls[int(size/2)][int(size/2)],'red',True) #cel cella pirosra grafika
    canvas.update() #megjlenitunk

def genBinTree(size):
    global walls
    walls = [[[1,1,1,1] for _ in range(size)] for _ in range(size)] #falak toltese, ezekbol veszunk majd el
    for y in range(0,size,1): #midnket iranyban vegigiteralunk a matrixon
        for x in range(0,size,1):
            neighbors=getAll(x,y,size) #begyujtjuk az osszes szomszedot
            if ((x-1,y)) in neighbors: #toroljuk a bal oldalit
                neighbors.remove((x-1,y))
            if ((x,y-1)) in neighbors: #toroljuk a folsot
                neighbors.remove((x,y-1))
            if neighbors: #ha maradt szomszed
                nx,ny=random.choice(neighbors) #random valasztunk
                updateWalls(nx, ny,x,y) #falakat frissitjuk
            modifyCell(x,y,walls[x][y],'#777777',True) #az eredeti cellat szinezzuk
                

    modifyCell(0,0,walls[0][0],'green',True) #kezdo cella zoldre grafika 
    modifyCell(int(size/2),int(size/2),walls[int(size/2)][int(size/2)],'red',True) #cel cella pirosra grafika
    canvas.update() #megjlenitunk

def solveDF(size):
    global walls
    xd,yd=(int(size/2),int(size/2))
    node=Node(0,0,0)
    stack = [node] #stack-be taroljuk a bejart utat, viszalepeskor popoljuk a cellakat
    visited=set()
    while (node.x,node.y)!=(xd,yd):
        parent=node #elozo node a kovetkezo szuloje
        neighbors = getPassage(node, walls, visited) #lehetseges utat keressuk
        if neighbors: #ha van
            x, y = random.choice(neighbors) #random valsztunk szomszedot
            node=Node(x,y,parent) #node inicializalas
            modifyCell(node.x,node.y,walls[node.x][node.y],'blue',False) #grafika update
            if realtime.get():
                time.sleep(0.1/size)
            visited.add((node.x,node.y)) #latogatottba tesszuk
            stack.append(node) #stackbe tesszuk
        else:
            stack.pop() #stackbol kivesszuk
            node=stack[-1] #uj node a stack legfolsoje
    modifyCell(xd,yd,walls[xd][yd],'orange',False)
    for node in stack:
        modifyCell(node.x,node.y,walls[node.x][node.y],'orange',False) #grafika update
    modifyCell(0,0,walls[0][0],'orange',False)
    
    modifyCell(0,0,walls[0][0],'green',True) #kezdo cella zoldre grafika 
    modifyCell(int(size/2),int(size/2),walls[int(size/2)][int(size/2)],'red',True) #cel cella pirosra grafika

    path=int(len(stack))
    allcells=len(visited)+1

    LABpathval.config(text=str(path)) #feliratok
    LABvisitedval.config(text=str(allcells))

    updateStats("DF",path,allcells)

def solveBF(size):
    global walls
    xd,yd=(int(size/2),int(size/2)) #celcella
    node=Node(0,0,0) #kezdocella
    visited=set() #latogatott cellak
    thislayer=set() #adott reteg
    nextlayer=set() #kovetkezo reteg
    thislayer.add(node) #adott reteghez hozzaadjuk a kezdocellat
    stop=False #megallitas indikator
    while stop==False: #mig nem akarunk megallni
        for nodes in thislayer: #adott retegben node-okat vegignezzuk
            if nodes.x==xd and nodes.y==yd: #ha valamelyik node cel
                stop=True #megallunk
                finish=nodes #vegcellat eltaroljuk
                break #nem keresunk tovabb
            visited.add((nodes.x,nodes.y)) #hozzaadjuk a latogatotthoz
            modifyCell(nodes.x,nodes.y,walls[nodes.x][nodes.y],'blue',False) #grafika update
            if realtime.get():
                time.sleep(0.1/size)
            children=getPassage(nodes,walls,visited) #eloallitjuk a gyerekeket
            for child in children:
                x,y=child
                nextlayer.add(Node(x,y,nodes)) #gyerekeket hozzadjuk a kovetkezo reteghez
        thislayer.clear() #adott reteget toroljuk
        for i in nextlayer: #kovetkezo reteg lesz az adott reteg
            thislayer.add(i)
        nextlayer.clear() #kovetkezo reteget toroljuk, ogy lehessen tolteni
    pathlength=1
    modifyCell(xd,yd,walls[xd][yd],'orange',False)
    while finish.level!=0: #mutatjuk a talalt utvonalat
         pathlength+=1
         modifyCell(finish.x,finish.y,walls[finish.x][finish.y],'orange',False)
         finish=finish.parent
    modifyCell(0,0,walls[0][0],'orange',False)

    modifyCell(0,0,walls[0][0],'green',True) #kezdo cella zoldre grafika 
    modifyCell(int(size/2),int(size/2),walls[int(size/2)][int(size/2)],'red',True) #cel cella pirosra grafika

    allcells=len(visited)+1

    LABpathval.config(text=str(pathlength)) #feliratok
    LABvisitedval.config(text=str(allcells))

    updateStats("BF",pathlength,allcells)

def solveDFID(size):
    global walls
    xd,yd=(int(size/2),int(size/2))
    limit=size-3
    cntr=0
    node=Node(0,0,0)
    stop=False
    while stop!=True: #amig nem allitjuk le 
        clear()
        node=Node(0,0,0)
        visited=set()
        stack=[node]
        while len(stack)>0:
            parent=node
            neighbors=getPassage(node,walls,visited)
            if node.x==xd and node.y==yd:
                stop=True
                finish=node
                break
            if neighbors and node.level<limit: #gyakorlatilag egyetlen elteres a DF-hez kepest, hogy limitet is nezunk
                x,y=random.choice(neighbors)
                node=Node(x,y,parent,xd,yd) #node inicializalas
                modifyCell(node.x,node.y,walls[node.x][node.y],'blue',False) #grafika update
                visited.add((node.x,node.y)) #latogatottba tesszuk
                stack.append(node) #stackbe tesszuk
            else:
                stack.pop()
                if len(stack)>0:
                    node=stack[-1]
        limit+=1
            
    pathlength=1
    modifyCell(xd,yd,walls[xd][yd],'orange',False)
    while finish.level!=0: #mutatjuk a talalt utvonalat
         pathlength+=1
         modifyCell(finish.x,finish.y,walls[finish.x][finish.y],'orange',False)
         finish=finish.parent
    modifyCell(0,0,walls[0][0],'orange',False)

    modifyCell(0,0,walls[0][0],'green',True) #kezdo cella zoldre grafika 
    modifyCell(int(size/2),int(size/2),walls[int(size/2)][int(size/2)],'red',True) #cel cella pirosra grafika

    allcells=len(visited)+1

    LABpathval.config(text=str(pathlength)) #feliratok
    LABvisitedval.config(text=str(allcells))

    updateStats("DFID",pathlength,allcells)

def solveAstar(size):
    global walls
    xd,yd=(int(size/2),int(size/2))
    znode=Node(0,0,0,xd,yd) #celertekkel inicializalt node, hogy legyen heurisztikus fv
    visited=set()
    visited.add(znode)
    possible=[znode]
    node=znode
    while (node.x==xd and node.y==yd)==False:
        oldnode=node
        for i in possible: #megkeressuk a legkisebb fuggvenyu node-ot
            if i.func<=node.func and i not in visited:
                node=i
        if node==oldnode: #ha nem talatunk jobbat, eroltetjuk hogy masik legyen
            node=possible[-1]
        else: #ha van jobb, az uj mar nem lehetseges
            possible.remove(node)
        modifyCell(node.x,node.y,walls[node.x][node.y],'blue',False)
        if realtime.get(): #lassitunk a futason, hogy szemleletes legyen
                time.sleep(0.1/size)
        visited.add(node) #bejarjuk
        neighbors = getPassage(node, walls, visited) #lehetseges szomszedokat vizsgaljuk
        for i in neighbors:
            (x,y)=i
            possible.append(Node(x,y,node,xd,yd)) #szomszedok lehetsegesek

    pathlength=0
    modifyCell(xd,yd,walls[xd][yd],'orange',False)
    while node.level!=0: #mutatjuk a talalt utvonalat
        pathlength+=1
        modifyCell(node.x,node.y,walls[node.x][node.y],'orange',False)
        node=node.parent
    modifyCell(0,0,walls[0][0],'orange',False)

    modifyCell(0,0,walls[0][0],'green',True) #kezdo cella zoldre grafika 
    modifyCell(int(size/2),int(size/2),walls[int(size/2)][int(size/2)],'red',True) #cel cella pirosra grafika

    allcells=len(visited)+1

    LABpathval.config(text=str(pathlength+1)) #feliratok
    LABvisitedval.config(text=str(allcells))

    updateStats("Astar",pathlength+1,allcells)

def solveIDAstar(size):
    global walls
    xd,yd=(int(size/2),int(size/2))
    znode=Node(0,0,0,xd,yd)
    visited=set()
    limit=size/2
    node=znode
    stop=False
    while stop==False: #limitet novelo iteraco, ami koreboleli az A* ciklusat
        possible=[znode]
        node=znode
        while len(possible)!=0:
            if node.x==xd and node.y==yd:
                stop=True
                break
            oldnode=node
            for i in possible:
                if i.func<=node.func and i not in visited:
                    node=i
                if i in visited:
                    possible.remove(i)
            if node==oldnode:
                if len(possible)>0:
                    node=possible[-1]
                else:
                    break
            else:
                possible.remove(node)
            modifyCell(node.x,node.y,walls[node.x][node.y],'blue',False)
            visited.add(node)
            neighbors = getPassage(node, walls, visited)
            for i in neighbors:
                (x,y)=i
                newnode=Node(x,y,node,xd,yd)
                if newnode.level<=limit:
                    possible.append(newnode)
        limit+=1
        if stop==False:
            visited.clear()
            clear()

    pathlength=0
    modifyCell(xd,yd,walls[xd][yd],'orange',False)
    while node.level!=0: #mutatjuk a talalt utvonalat
        pathlength+=1
        modifyCell(node.x,node.y,walls[node.x][node.y],'orange',False)
        node=node.parent
    modifyCell(0,0,walls[0][0],'orange',False)

    modifyCell(0,0,walls[0][0],'green',True) #kezdo cella zoldre grafika 
    modifyCell(int(size/2),int(size/2),walls[int(size/2)][int(size/2)],'red',True) #cel cella pirosra grafika

    allcells=len(visited)+1

    LABpathval.config(text=str(pathlength+1)) #feliratok
    LABvisitedval.config(text=str(allcells))

    updateStats("IDAstar",pathlength+1,allcells)

def getPossible(x, y, maze, size):
    neighbors = []  #meg nem latogatott szomszedoknak fenntartott lista
    dir = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # lehetseges lepesi iranyok

    for dx, dy in dir: #minden iranyt megvizsgalunk
        nx, ny = x + dx, y + dy  #az adott iranyban levo szomszed koordinatai
        if 0 <= nx < size and 0 <= ny < size and maze[nx][ny] == 1: #ha a szomszed a hatarokon belul van es nem latogatott
            neighbors.append((nx, ny))  # hozzaadjuk a listahoz a koordinatait
        elif 0 <= nx < size and 0 <= ny < size and random.randint(1,int(size*loopModifier))==1: #neha megengedunk egy olyat is, hogy felulirjon cellat, hogy legyenek alternativ utan
            neighbors.append((nx,ny))

    return neighbors  #visszaadjuk a szomszedok listajat

def getAll(x, y, size):
    neighbors = []  #meg nem latogatott szomszedoknak fenntartott lista
    dir = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # lehetseges lepesi iranyok

    for dx, dy in dir: #minden iranyt megvizsgalunk
        nx, ny = x + dx, y + dy  #az adott iranyban levo szomszed koordinatai
        if 0 <= nx < size and 0 <= ny < size: #ha a szomszed a hatarokon belul van
            neighbors.append((nx, ny))  # hozzaadjuk a listahoz a koordinatait

    return neighbors  #visszaadjuk a szomszedok listajat

def updateWalls(nx, ny, x, y):
    global walls
    if nx==x+1: #ha a szomszed cella az eredetitol jobbra van
        walls[nx][ny][1]=0 #szomszed bal falanak torlese
        walls[x][y][0]=0#cella jobb falanak torlese
    if nx==x-1: #ha a szomszed cella az eredetitol balra van
        walls[nx][ny][0]=0 #hasonloan az elso esethez
        walls[x][y][1]=0
    if ny==y+1: #ha a szomszed cella az eredetitol lefele van
        walls[nx][ny][2]=0
        walls[x][y][3]=0
    if ny==y-1: #ha a szomszed cella az eredetitol felfele van
        walls[nx][ny][3]=0
        walls[x][y][2]=0

def getPassage(node,walls, visited):
    x=node.x
    y=node.y
    dir = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)] #lehetseges iranyok
    possible=[]
    if walls[x][y][0]==0 and dir[0] and dir[0] not in visited: #ha nem latogatott, hozzaadjuk a lehetsegesekhez
        possible.append(dir[0])
    if walls[x][y][1]==0 and dir[1] and dir[1] not in visited:
        possible.append(dir[1])
    if walls[x][y][3]==0 and dir[2] and dir[2] not in visited:
        possible.append(dir[2])
    if walls[x][y][2]==0 and dir[3] and dir[3] not in visited:
        possible.append(dir[3])
    return possible #visszadjuk a lehetsegeseket

def initCells(size):
    global visual
    visual = [[[1,[1,1,1,1]] for _ in range(size)] for _ in range(size)]
    for x in range(0,size,1):
        for y in range(0,size,1):
            points=[10+(x*cellSize),10+(y*cellSize),10+((x+1)*cellSize),10+((y+1)*cellSize)]
            visual[x][y][0]=canvas.create_rectangle(points[0],points[1],points[2],points[3], fill="#dddddd", outline="black", width=0)
            visual[x][y][1][0]=canvas.create_line(points[0]+cellSize, points[1], points[2], points[3], fill="black", state='hidden', width=2)
            visual[x][y][1][1]=canvas.create_line(points[0], points[1], points[2]-cellSize, points[3], fill="black", state='hidden', width=2)
            visual[x][y][1][2]=canvas.create_line(points[0], points[1], points[2], points[3]-cellSize, fill="black", state='hidden', width=2)
            visual[x][y][1][3]=canvas.create_line(points[0], points[1]+cellSize, points[2], points[3], fill="black", state='hidden', width=2)
    canvas.create_rectangle(10, 10, 510, 510, outline="black", width=4, fill=None)#labirintus kulso hataranak frissitese, hogy ne legyen folotte szines cella

def modifyCell(x,y,walls,color,gen):
    global var
    if gen==True:
        canvas.itemconfig(visual[x][y][0], fill=color)
        if walls[0]==1:#falak vizsgalata, ha van, huzunk oda vonalat
            canvas.itemconfig(visual[x][y][1][0], state='normal')
        else:
            canvas.itemconfig(visual[x][y][1][0], state='hidden')
        if walls[1]==1:
            canvas.itemconfig(visual[x][y][1][1], state='normal')
        else:
            canvas.itemconfig(visual[x][y][1][1], state='hidden')
        if walls[2]==1:
            canvas.itemconfig(visual[x][y][1][2], state='normal')
        else:
            canvas.itemconfig(visual[x][y][1][2], state='hidden')
        if walls[3]==1:
            canvas.itemconfig(visual[x][y][1][3], state='normal')
        else:
            canvas.itemconfig(visual[x][y][1][3], state='hidden')
    if gen==False:
        canvas.itemconfig(visual[x][y][0], fill=color, outline="black", width=0)
    if realtime.get(): #ha real time futtatunk, frissitse is a canvast. A real time futtatas latvanyos, de sokkal lassabb
        canvas.update()

def generate():
    global cellSize
    global size
    global loopModifier
    canvas.delete(all)
    size=int(entry1.get())
    if size>100: #50-re limitaljuk a laibirintus oldalhosszat eroforras es felbontas miatt
        size=100
        entry1.delete(0,100)
        entry1.insert(0, size)
    loopModifier=int(entry2.get())
    if loopModifier<1 or loopModifier>100: #50-re limitaljuk a laibirintus oldalhosszat eroforras es felbontas miatt
        loopModifier=3
        entry2.delete(0,100)
        entry2.insert(0, 3)
    cellSize=500/size
    initCells(size)
    if selector1.get()==options[0]: #generalo algortmusok kozul valasztunk
        genD1st(size)
    if selector1.get()==options[1]: #generalo algortmusok kozul valasztunk
        genPrim(size)
    if selector1.get()==options[2]: #generalo algortmusok kozul valasztunk
        genBinTree(size)

def solve():
    clear()
    if selector2.get()==options2[0]: #megoldo algortmusok kozul valasztunk
        solveDF(size)
    if selector2.get()==options2[1]: #megoldo algortmusok kozul valasztunk
        solveBF(size)
    if selector2.get()==options2[2]: #megoldo algortmusok kozul valasztunk
        solveDFID(size)
    if selector2.get()==options2[3]: #megoldo algortmusok kozul valasztunk
        solveAstar(size)
    if selector2.get()==options2[4]: #megoldo algortmusok kozul valasztunk
        solveIDAstar(size)

def clear():
    real=False
    if realtime.get(): #a torlest ne kelljen kivarni
        checkbox1.deselect()
        real=True
    xd,yd=(int(size/2),int(size/2)) #letorli a megoldast (random megoldot lehessen tobbszor futtatni azonos labirintuson)
    for x in range(0,size,1):
        for y in range(0,size,1):
            if (x,y) != (0,0) and (x,y)!=(xd,yd):
                modifyCell(x,y,walls[x][y],"#777777",True)
    modifyCell(0,0,walls[0][0],"green",True)      
    modifyCell(xd,yd,walls[xd][yd],"red",True)      
    if real==True:
        checkbox1.select()
    LABpathval.config(text="-")
    LABvisitedval.config(text="-")

def exportcsv():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    dateTime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    name = f'{dateTime}.csv' #eloallitjuk a filenevet
    path = os.path.join(script_directory,"mazes", name) #eloallitjuk a konyvtarat
    csvfile=open(path, 'w')
    for row in walls: #bemasoljuk a sorokat a csv-be
        csvfile.write(','.join(map(str, row)) + '\n')
    time.sleep(0.75)#hogy legyen ido menteni

def importcsv():
    global walls
    global cellSize
    canvas.delete("all") #letoroljuk a canvast
    canvas.create_rectangle(10, 10, 510, 510, outline="black", width=4, fill='#dddddd')
    filename=filedialog.askopenfilename()
    csvfile=open(filename, 'r')
    wall=[]
    size=0
    for x in csvfile: #meret meghatarozas
        size+=1
    cellSize=500/size
    walls = [[[0,0,0,0] for _ in range(size)] for _ in range(size)] #falak toltese, ezekbol veszunk majd el
    csvfile=open(filename, 'r')
    xc=0
    yc=0
    for x in csvfile: #vegigiteralunk es betoltunk a walls-ba
        y=x.split(',')
        wall=[]
        for value in y:
            value=value.replace("[","")
            value=value.replace("]","")
            value=value.replace("\n","")
            value=value.replace(" ","")
            wall.append(int(value))
            if len(wall)==4:
                walls[xc][yc]=wall
                wall=[]
                yc+=1
        xc+=1
        yc=0
    for x in range(0,xc,1): #megjelenitunk
            for y in range(0,xc,1):
                modifyCell(x,y,walls[x][y],"#777777",True)
    modifyCell(0,0,walls[0][0],'green',True) #kezdo cella zoldre grafika 
    modifyCell(int(size/2),int(size/2),walls[int(size/2)][int(size/2)],'red',True) #cel cella pirosra grafika

def updateStats(tech,path,visited):
    global statDF
    global statBF
    global statDFID
    global statAstar
    global statIDAstar
    cntr,pathavg,visitedavg=0,0,0
    if tech=="DF": #ha az adott algoritmussal oldottuk meg
        statDF.append((path,visited)) #hozzaadjuk a merest
        for stat in statDF: #atlagoljuk az etekeket
            pathavg+=stat[0]
            visitedavg+=stat[1]
            cntr+=1
        visitedavg=visitedavg/cntr #atlagot szamolunk
        pathavg=pathavg/cntr
        LABavgpathDF.config(text=str(round(pathavg,1))) #feliratok
        LABavgvisitedDF.config(text=str(round(visitedavg,1))) #feliratok
    if tech=="BF":
        statBF.append((path,visited))
        for stat in statBF:
            pathavg+=stat[0]
            visitedavg+=stat[1]
            cntr+=1
        visitedavg=visitedavg/cntr
        pathavg=pathavg/cntr
        LABavgpathBF.config(text=str(round(pathavg,1))) #feliratok
        LABavgvisitedBF.config(text=str(round(visitedavg,1))) #feliratok
    if tech=="DFID":
        statDF.append((path,visited))
        for stat in statDF:
            pathavg+=stat[0]
            visitedavg+=stat[1]
            cntr+=1
        visitedavg=visitedavg/cntr
        pathavg=pathavg/cntr
        LABavgpathDFID.config(text=str(round(pathavg,1))) #feliratok
        LABavgvisitedDFID.config(text=str(round(visitedavg,1))) #feliratok
    if tech=="Astar":
        statAstar.append((path,visited))
        for stat in statAstar:
            pathavg+=stat[0]
            visitedavg+=stat[1]
            cntr+=1
        visitedavg=visitedavg/cntr
        pathavg=pathavg/cntr
        LABavgpathAstar.config(text=str(round(pathavg,1))) #feliratok
        LABavgvisitedAstar.config(text=str(round(visitedavg,1))) #feliratok
    if tech=="IDAstar":
        statIDAstar.append((path,visited))
        for stat in statIDAstar:
            pathavg+=stat[0]
            visitedavg+=stat[1]
            cntr+=1
        visitedavg=visitedavg/cntr
        pathavg=pathavg/cntr
        LABavgpathIDAstar.config(text=str(round(pathavg,1))) #feliratok
        LABavgvisitedIDAstar.config(text=str(round(visitedavg,1))) #feliratok

def clearStats():
    global statDF
    global statBF
    global statDFID
    global statAstar
    global statIDAstar

    statDF.clear()
    statBF.clear()
    statDFID.clear()
    statAstar.clear()
    statIDAstar.clear()


    LABavgpathDF.config(text="-") #feliratok
    LABavgvisitedDF.config(text="-") #feliratok
    LABavgpathBF.config(text="-") #feliratok
    LABavgvisitedBF.config(text="-") #feliratok
    LABavgpathDFID.config(text="-") #feliratok
    LABavgvisitedDFID.config(text="-") #feliratok
    LABavgpathAstar.config(text="-") #feliratok
    LABavgvisitedAstar.config(text="-") #feliratok
    LABavgpathIDAstar.config(text="-") #feliratok
    LABavgvisitedIDAstar.config(text="-") #feliratok

#tkinter modulok a UI-hoz

root = tk.Tk()
root.title("Maze visualization")
root.state("zoomed")

title=tk.Label(root,text='Maze generator and solver', font=("Arial", 20, "bold"))

frameu=tk.Frame(root)

LABmazesize = tk.Label(frameu, text="Maze size:")
entry1 = tk.Entry(frameu)
entry1.insert(0, "16")

LABgenalgo = tk.Label(frameu, text="Generating algorithm:")
options = ['Randomized depth first', 'Prim\'s', 'Binary tree']
selector1 = ttk.Combobox(frameu, values=options)
selector1.set(options[0])

LABsolvealgo = tk.Label(frameu, text="Solving algorithm:")
options2 = ['Depth first','Breadth first','Depth first with ID', 'A*', 'IDA*']
selector2 = ttk.Combobox(frameu, values=options2)
selector2.set(options2[0])

button1 = tk.Button(frameu, text="Generate", command=generate)
button2 = tk.Button(frameu, text="Solve", command=solve)
button3 = tk.Button(frameu, text="Clear", command=clear)
button4 = tk.Button(frameu, text="Import csv", command=importcsv)

realtime=tk.IntVar()
checkbox1 = tk.Checkbutton(frameu,text='Real time run', variable=realtime)

export=tk.IntVar()
button5=tk.Button(frameu,text="Export csv", command=exportcsv)

LABloopmod = tk.Label(frameu, text="Loop modifier:")
entry2 = tk.Entry(frameu)
entry2.insert(0, "5")

LABvisitedtxt=tk.Label(frameu, text="Visited cells:")
LABpathtxt=tk.Label(frameu, text="Path length:")
LABvisitedval=tk.Label(frameu, text="-")
LABpathval=tk.Label(frameu, text="-")

canvas = tk.Canvas(root, width=520, height=520)
canvas.create_rectangle(10, 10, 510, 510, outline="black", width=4, fill='#dddddd')


framel=tk.Frame(root)


LABavg =tk.Label(framel,text='Averages', font=("Arial", 16, "bold"))
LABalgo =tk.Label(framel,text='algorithm', font=("Arial", 12, "bold"))
LABalgoDF=tk.Label(framel, text="Depth first:")
LABalgoBF=tk.Label(framel, text="Breadth first:")
LABalgoDFID=tk.Label(framel, text="Depth first with ID:")
LABalgoAstar=tk.Label(framel, text="A*:")
LABalgoIDAstar=tk.Label(framel, text="IDA*:")
LABavgpath=tk.Label(framel, text="path length", font=("Arial", 12, "bold"))
LABavgpathDF=tk.Label(framel, text="-")
LABavgpathBF=tk.Label(framel, text="-")
LABavgpathDFID=tk.Label(framel, text="-")
LABavgpathAstar=tk.Label(framel, text="-")
LABavgpathIDAstar=tk.Label(framel, text="-")
LABavgvisited=tk.Label(framel, text="cells visited", font=("Arial", 12, "bold"))
LABavgvisitedDF=tk.Label(framel, text="-")
LABavgvisitedBF=tk.Label(framel, text="-")
LABavgvisitedDFID=tk.Label(framel, text="-")
LABavgvisitedAstar=tk.Label(framel, text="-")
LABavgvisitedIDAstar=tk.Label(framel, text="-")
clearavg=tk.Button(framel,text="Clear averages", command=clearStats)

#Grid-be rendezes

title.grid(row=0, column=0, padx=20, pady=5)
frameu.grid(row=1,column=0, padx=20, pady=0)
canvas.grid(row=0, rowspan=3, column=1, padx=20, pady=50)
framel.grid(row=2,column=0, padx=20, pady=0)

LABmazesize.grid(row=0,column=0,padx=10, pady=5)
entry1.grid(row=0, column=1, padx=10, pady=5)
LABgenalgo.grid(row=1,column=0,padx=10, pady=5)
selector1.grid(row=1, column=1, padx=10, pady=5)
LABsolvealgo.grid(row=2,column=0,padx=10, pady=5)
selector2.grid(row=2, column=1, padx=10, pady=5)
button1.grid(row=3, column=0, padx=10, pady=20)
button2.grid(row=3, column=1, padx=10, pady=20)
button3.grid(row=4, column=0, padx=10, pady=5)
button4.grid(row=4, column=1, padx=10, pady=5)
checkbox1.grid(row=5, column=0, padx=10, pady=20)
button5.grid(row=5, column=1, padx=10, pady=20)
LABloopmod.grid(row=6,column=0,padx=0,pady=10)
entry2.grid(row=6,column=1,padx=0,pady=10)
LABvisitedtxt.grid(row=7, column=0, padx=0, pady=0)
LABvisitedval.grid(row=8, column=0, padx=0, pady=0)
LABpathtxt.grid(row=7, column=1, padx=0, pady=0)
LABpathval.grid(row=8, column=1, padx=0, pady=0)


LABavg .grid(row=0, column=0, padx=0, pady=0)

LABalgo .grid(row=1, column=0, padx=2, pady=0)
LABalgoDF.grid(row=2, column=0, padx=2, pady=0)
LABalgoBF.grid(row=3, column=0, padx=2, pady=0)
LABalgoDFID.grid(row=4, column=0, padx=2, pady=0)
LABalgoAstar.grid(row=5, column=0, padx=2, pady=0)
LABalgoIDAstar.grid(row=6, column=0, padx=2, pady=0)

LABavgpath.grid(row=1, column=1, padx=2, pady=0)
LABavgpathDF.grid(row=2, column=1, padx=2, pady=0)
LABavgpathBF.grid(row=3, column=1, padx=2, pady=0)
LABavgpathDFID.grid(row=4, column=1, padx=2, pady=0)
LABavgpathAstar.grid(row=5, column=1, padx=2, pady=0)
LABavgpathIDAstar.grid(row=6, column=1, padx=2, pady=0)

LABavgvisited.grid(row=1, column=2, padx=2, pady=0)
LABavgvisitedDF.grid(row=2, column=2, padx=2, pady=0)
LABavgvisitedBF.grid(row=3, column=2, padx=2, pady=0)
LABavgvisitedDFID.grid(row=4, column=2, padx=2, pady=0)
LABavgvisitedAstar.grid(row=5, column=2, padx=2, pady=0)
LABavgvisitedIDAstar.grid(row=6, column=2, padx=2, pady=0)

clearavg.grid(row=7, column=0, padx=10, pady=10)

initCells(size)

root.mainloop()