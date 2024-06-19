import tkinter as tk
from tkinter import ttk, filedialog #combobox miatt kell
import random 
from datetime import datetime
import time
import os

#alapveto valtozok inicializalasa
loopModifier=1
cellSize=50
size=10
walls=[] #ebbe tarolodnak a falak. 2D matrix, mely minden cellahoz a specifikacio szerint rendeli a falait
#statisztikakat tarolo listak
statDF=[]
statBF=[]
statDFID=[]
statIDAstar=[]

class Node:
    def __init__(self,x,y,parent): # cellak tarolasara valo osztaly
        self.x=x
        self.y=y
        self.parent=parent
        if parent ==0:
            self.level=0
        else:
            self.level=parent.level+1
    def __str__(self):
        return f"{self.x},{self.y} - {self.level}"

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
            visited.add((node.x,node.y)) #latogatottba tesszuk
            stack.append(node) #stackbe tesszuk
        else:
            stack.pop() #stackbol kivesszuk
            node=stack[-1] #uj node a stack legfolsoje
    for node in stack:
        modifyCell(node.x,node.y,walls[node.x][node.y],'orange',False) #grafika update

    modifyCell(0,0,walls[0][0],'green',True) #kezdo cella zoldre grafika 
    modifyCell(int(size/2),int(size/2),walls[int(size/2)][int(size/2)],'red',True) #cel cella pirosra grafika

    path=int(len(stack))
    allcells=len(visited)+1

    label7.config(text=str(path)) #feliratok
    label6.config(text=str(allcells))

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
            children=getPassage(nodes,walls,visited) #eloallitjuk a gyerekeket
            for child in children:
                x,y=child
                nextlayer.add(Node(x,y,nodes)) #gyerekeket hozzadjuk a kovetkezo reteghez
        thislayer.clear() #adott reteget toroljuk
        for i in nextlayer: #kovetkezo reteg lesz az adott reteg
            thislayer.add(i)
        nextlayer.clear() #kovetkezo reteget toroljuk, ogy lehessen tolteni
    pathlength=1
    while finish.level!=0: #mutatjuk a talalt utvonalat
         pathlength+=1
         modifyCell(finish.x,finish.y,walls[finish.x][finish.y],'orange',False)
         finish=finish.parent
    modifyCell(0,0,walls[0][0],'green',True) #kezdo cella zoldre grafika 
    modifyCell(int(size/2),int(size/2),walls[int(size/2)][int(size/2)],'red',True) #cel cella pirosra grafika

    allcells=len(visited)+1

    label7.config(text=str(pathlength)) #feliratok
    label6.config(text=str(allcells))

    updateStats("BF",pathlength,allcells)

def solveDFID(size):
    global walls
    xd,yd=(int(size/2),int(size/2))
    znode=Node(0,0,0)
    finish=znode
    visited=set()
    stop=False
    print("-----")
    for limit in range(size,size*size,1):
        print("---")
        stack = [znode]
        stack2=[(znode.x,znode.y)]
        cntr=0
        visited=set()
        while len(stack)>0:
            node=stack[-1]
            stack.pop()
            stack2.pop()
            if (node.x,node.y) not in visited:
                modifyCell(node.x,node.y,walls[node.x][node.y],'blue',False)
            visited.add((node.x,node.y))
            neighbors = getPassage(node, walls, stack)
            for neighbor in neighbors:
                cntr+=1
                x,y=neighbor
                newnode=Node(x,y,node)
                if newnode.level<=limit:
                    stack.append(newnode)
                    stack2.append((newnode.x,newnode.y))
                if newnode.x==xd and newnode.y==yd:
                    stop=True
                    finish=newnode
                    break
            if stop==True:
                break
        print(cntr)
        if stop==True:
            break
        
    pathlength=1
    while finish.level!=0: #mutatjuk a talalt utvonalat
         pathlength+=1
         modifyCell(finish.x,finish.y,walls[finish.x][finish.y],'orange',False)
         finish=finish.parent
    

    modifyCell(0,0,walls[0][0],'green',True) #kezdo cella zoldre grafika 
    modifyCell(int(size/2),int(size/2),walls[int(size/2)][int(size/2)],'red',True) #cel cella pirosra grafika

    allcells=len(visited)+1

    label7.config(text=str(pathlength)) #feliratok
    label6.config(text=str(allcells))

    updateStats("DFID",pathlength,allcells)

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

def modifyCell(x,y,walls,color,gen):
    global var
    if gen==True:
        points=[10+(x*cellSize),10+(y*cellSize),10+((x+1)*cellSize),10+((y+1)*cellSize)]#cella pontjainak szamolasa
        canvas.create_rectangle(points[0],points[1],points[2],points[3], fill=color, outline="black", width=0)#cella generalasa
        if walls[0]==1:#falak vizsgalata, ha van, huzunk oda vonalat
            canvas.create_line(points[0]+cellSize, points[1], points[2], points[3], fill="black", width=2)
        if walls[1]==1:
            canvas.create_line(points[0], points[1], points[2]-cellSize, points[3], fill="black", width=2)
        if walls[2]==1:
            canvas.create_line(points[0], points[1], points[2], points[3]-cellSize, fill="black", width=2)
        if walls[3]==1:
            canvas.create_line(points[0], points[1]+cellSize, points[2], points[3], fill="black", width=2)
        canvas.create_rectangle(10, 10, 510, 510, outline="black", width=4, fill=None)#labirintus kulso hataranak frissitese, hogy ne legyen folotte szines cella
    if gen==False:
        shrink=500/size/4
        points=[10+(x*cellSize)+shrink,10+(y*cellSize)+shrink,10+((x+1)*cellSize)-shrink,10+((y+1)*cellSize-shrink)]#cella pontjainak szamolasa
        canvas.create_rectangle(points[0],points[1],points[2],points[3], fill=color, outline="black", width=0)#cella generalasa
        canvas.create_rectangle(10, 10, 510, 510, outline="black", width=4, fill=None)#labirintus kulso hataranak frissitese, hogy ne legyen folotte szines cella
    if realtime.get(): #ha real time futtatunk, frissitse is a canvast. A real time futtatas latvanyos, de sokkal lassabb
        canvas.update()

def generate():
    global cellSize
    global size
    size=int(entry1.get())
    if size>100: #50-re limitaljuk a laibirintus oldalhosszat eroforras es felbontas miatt
        size=100
        entry1.delete(0,100)
        entry1.insert(0, size)
    cellSize=500/size
    canvas.delete("all") #letoroljuk a canvast
    canvas.create_rectangle(10, 10, 510, 510, outline="black", width=4, fill='#dddddd')
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
    if real==True:
        checkbox1.select()
    label7.config(text="-")
    label6.config(text="-")

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
    canvas.delete("all") #letoroljuk a canvast
    canvas.create_rectangle(10, 10, 510, 510, outline="black", width=4, fill='#dddddd')
    filename=filedialog.askopenfilename()
    csvfile=open(filename, 'r')
    wall=[]
    size=0
    for x in csvfile: #meret meghatarozas
        size+=1
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
                modifyCell(x,y,walls[x][y],"#777777")
    modifyCell(0,0,walls[0][0],'green') #kezdo cella zoldre grafika 
    modifyCell(int(size/2),int(size/2),walls[int(size/2)][int(size/2)],'red') #cel cella pirosra grafika

def updateStats(tech,path,visited):
    global statDF
    global statBF
    global statDFID
    cntr,pathavg,visitedavg=0,0,0
    if tech=="DF": #ha az adott algoritmussal oldottuk meg
        statDF.append((path,visited)) #hozzaadjuk a merest
        for stat in statDF: #atlagoljuk az etekeket
            pathavg+=stat[0]
            visitedavg+=stat[1]
            cntr+=1
        visitedavg=visitedavg/cntr #atlagot szamolunk
        pathavg=pathavg/cntr
        label15.config(text=str(round(pathavg,1))) #feliratok
        label20.config(text=str(round(visitedavg,1))) #feliratok
    if tech=="BF":
        statBF.append((path,visited))
        for stat in statBF:
            pathavg+=stat[0]
            visitedavg+=stat[1]
            cntr+=1
        visitedavg=visitedavg/cntr
        pathavg=pathavg/cntr
        label16.config(text=str(round(pathavg,1))) #feliratok
        label21.config(text=str(round(visitedavg,1))) #feliratok
    if tech=="DFID":
        statDF.append((path,visited))
        for stat in statDF:
            pathavg+=stat[0]
            visitedavg+=stat[1]
            cntr+=1
        visitedavg=visitedavg/cntr
        pathavg=pathavg/cntr
        label17.config(text=str(round(pathavg,1))) #feliratok
        label22.config(text=str(round(visitedavg,1))) #feliratok
    

#tkinter modulok a UI-hoz

root = tk.Tk()
root.title("Maze")
root.state("zoomed")

frameu=tk.Frame(root)

label1 = tk.Label(frameu, text="Maze size:")
entry1 = tk.Entry(frameu)
entry1.insert(0, "10")

label2 = tk.Label(frameu, text="Generating algorithm:")
options = ['Randomized depth first', 'Prim\'s', 'Binary tree']
selector1 = ttk.Combobox(frameu, values=options)
selector1.set(options[0])

label3 = tk.Label(frameu, text="Solving algorithm:")
options2 = ['Depth first','Breadth first','Depth first with ID', 'Greedy', 'IDA*']
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

label4=tk.Label(frameu, text="Visited cells:")
label5=tk.Label(frameu, text="Path length:")
label6=tk.Label(frameu, text="-")
label7=tk.Label(frameu, text="-")

canvas = tk.Canvas(root, width=520, height=520)
canvas.create_rectangle(10, 10, 510, 510, outline="black", width=4, fill='#dddddd')


framel=tk.Frame(root)


label8 =tk.Label(framel,text='Averages', font=("Arial", 16, "bold"))
label9 =tk.Label(framel,text='algorithm', font=("Arial", 12, "bold"))
label10=tk.Label(framel, text="Depth first:")
label11=tk.Label(framel, text="Breadth first:")
label12=tk.Label(framel, text="Depth first with ID:")
label13=tk.Label(framel, text="IDA*:")
label14=tk.Label(framel, text="path length", font=("Arial", 12, "bold"))
label15=tk.Label(framel, text="-")
label16=tk.Label(framel, text="-")
label17=tk.Label(framel, text="-")
label18=tk.Label(framel, text="-")
label19=tk.Label(framel, text="cells visited", font=("Arial", 12, "bold"))
label20=tk.Label(framel, text="-")
label21=tk.Label(framel, text="-")
label22=tk.Label(framel, text="-")
label23=tk.Label(framel, text="-")

#Grid-be rendezes

frameu.grid(row=0,column=0, padx=20, pady=0)
canvas.grid(row=0, rowspan=2, column=1, padx=20, pady=50)
framel.grid(row=1,column=0, padx=20, pady=0)

label1.grid(row=0,column=0,padx=10, pady=5)
entry1.grid(row=0, column=1, padx=10, pady=5)
label2.grid(row=1,column=0,padx=10, pady=5)
selector1.grid(row=1, column=1, padx=10, pady=5)
label3.grid(row=2,column=0,padx=10, pady=5)
selector2.grid(row=2, column=1, padx=10, pady=5)
button1.grid(row=3, column=0, padx=10, pady=20)
button2.grid(row=3, column=1, padx=10, pady=20)
button3.grid(row=4, column=0, padx=10, pady=5)
button4.grid(row=4, column=1, padx=10, pady=5)
checkbox1.grid(row=5, column=0, padx=10, pady=20)
button5.grid(row=5, column=1, padx=10, pady=20)
label4.grid(row=7, column=0, padx=0, pady=0)
label5.grid(row=8, column=0, padx=0, pady=0)
label6.grid(row=7, column=1, padx=0, pady=0)
label7.grid(row=8, column=1, padx=0, pady=0)


label8 .grid(row=0, column=0, padx=0, pady=0)

label9 .grid(row=1, column=0, padx=2, pady=0)
label10.grid(row=2, column=0, padx=2, pady=0)
label11.grid(row=3, column=0, padx=2, pady=0)
label12.grid(row=4, column=0, padx=2, pady=0)
label13.grid(row=5, column=0, padx=2, pady=0)

label14.grid(row=1, column=1, padx=2, pady=0)
label15.grid(row=2, column=1, padx=2, pady=0)
label16.grid(row=3, column=1, padx=2, pady=0)
label17.grid(row=4, column=1, padx=2, pady=0)
label18.grid(row=5, column=1, padx=2, pady=0)

label19.grid(row=1, column=2, padx=2, pady=0)
label20.grid(row=2, column=2, padx=2, pady=0)
label21.grid(row=3, column=2, padx=2, pady=0)
label22.grid(row=4, column=2, padx=2, pady=0)
label23.grid(row=5, column=2, padx=2, pady=0)

root.mainloop()