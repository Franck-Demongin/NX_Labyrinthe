import time
from random import randint
import json

class Pile:
  def __init__(self):
      self.lst = []
  
  def is_empty(self):
        return self.lst == []
  
  def push(self, x):
        self.lst.append(x)

  def pop(self):
      if self.is_empty():
          raise ValueError("pile vide") 
      return self.lst.pop()

class Labyrinthe:

  def __init__(self):
    self.w = None
    self.h = None
    self.orientation = None
    self.tab = []

  def init(self, w, h, orientation, orientationStrength):
    self.w = w
    self.h = h
    self.orientation = orientation
    self.orientationStrength = orientationStrength
    self.tab = [[{'N': False, 'E': False, 'S': False, 'W': False, 'state': False} 
                for j in range(h)] 
                for i in range(w)]
    self.input = None
    self.output = None
    
    self._create()
  
  def _create(self):
    start_time = time.time()
    print('CREATE...')

    self.input = (0, randint(0, (self.h - 1)))

    pile = Pile()
    pile.push(self.input) 

    self.tab[self.input[0]][self.input[1]]['state'] = True
    
    while not pile.is_empty():
        i, j = pile.pop()
        v = []

        if j < self.h-1 and not self.tab[i][j+1]['state']:
            v.append('N')
        if i > 0 and not self.tab[i-1][j]['state']:
            v.append('W')
        if j > 0 and not self.tab[i][j-1]['state']:
            v.append('S')
        if i < self.w-1 and not self.tab[i+1][j]['state']:
            v.append('E') 
        
        if len(v) > 1:
            pile.push((i, j)) 
        
        if len(v) > 0:
            c = v[randint(0, len(v) - 1)] 
            test = False
            o = None
            if self.orientation != 'NONE':
                test = True
                o = 'W'
                if self.orientation == 'X':
                    o = 'N'
            while test:
                if c == o:
                    c = v[randint(0, len(v) - 1)] 
                    if not randint(0, self.orientationStrength):
                        test = False
                else: 
                    test = False
            if c == 'N':
                self.tab[i][j]['N'] = True
                self.tab[i][j+1]['S'] = True
                self.tab[i][j+1]['state'] = True 
                pile.push((i, j+1))
            elif c == 'W':
                self.tab[i][j]['W'] = True 
                self.tab[i-1][j]['E'] = True 
                self.tab[i-1][j]['state'] = True 
                pile.push((i-1, j))
            elif c == 'S':
                self.tab[i][j]['S'] = True 
                self.tab[i][j-1]['N'] = True 
                self.tab[i][j-1]['state'] = True 
                pile.push((i, j-1))
            else:
                self.tab[i][j]['E'] = True 
                self.tab[i+1][j]['W'] = True 
                self.tab[i+1][j]['state'] = True 
                pile.push((i+1, j))
    
    print("--- %s seconds ---" % (time.time() - start_time))
    print('END CREATE')
      
  def getCell(self, x, y):
    return self.tab[x][y]

  def toString(self, action = 0):
    if action == 0:
        return json.dumps(self.tab)
    if action == 1:
        ids = []
        for i in range(self.w):
            for j in range(self.h):
                if i < self.w - 1 and self.tab[i][j]['E']:
                    if (i,j,'E') not in ids:
                        ids.append((i,j,'E'))
                if j < self.h -1 and self.tab[i][j]['N']:
                    if (i,j,'N') not in ids:
                        ids.append((i,j,'N')) 
    
        return json.dumps(ids)
    if action == 2:
        ids = []
        for i in range(self.w):
            for j in range(self.h):
                wls = []
                if i < self.w - 1 and self.tab[i][j]['E']:
                    wls.append('E')
                if j < self.h -1 and self.tab[i][j]['N']:
                    wls.append('N')
                if wls != []:
                    cell = [i, j]
                    for w in wls:
                        cell.append(w) 
                    ids.append(cell)
        
        return json.dumps(ids)
    if action == 3:
        ids = []
        for i in range(self.w):
            for j in range(self.h):
                wls = []
                if i < self.w - 1 and self.tab[i][j]['E']:
                    wls.append('E')
                if j < self.h -1 and self.tab[i][j]['N']:
                    wls.append('N')
                if wls != []:
                    cell = [i, j]
                    for w in wls:
                        cell.append(w) 
                    ids.append(cell)
        return json.dumps(ids, separators=(',', ':'))
    if action == 4:
        ids = []
        for i in range(self.w):
            for j in range(self.h):
                wls = []
                if i < self.w - 1 and self.tab[i][j]['E']:
                    wls.append('E')
                if j < self.h -1 and self.tab[i][j]['N']:
                    wls.append('N')
                if wls != []:
                    ids.append(i)
                    ids.append(j)
                    for w in wls:
                        ids.append(w)
    
        return json.dumps(ids, separators=(',', ':'))
    if action == 5:
        ids = []
        for i in range(self.w):
            for j in range(self.h):
                wls = []
                if i < self.w - 1 and self.tab[i][j]['E']:
                    wls.append('E')
                if j < self.h -1 and self.tab[i][j]['N']:
                    wls.append('N')
                if wls != []:
                    ids.append(i)
                    ids.append(j)
                    x = 0
                    for w in wls:
                        if w == 'E':
                            x += 1
                        else:
                            x += 2
                    ids.append(x)
    
        return json.dumps(ids, separators=(',', ':'))

  