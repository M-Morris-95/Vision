import csv
import numpy as np

def DefTemps():
    Templates = np.zeros((36,20,20))
    i = 1
    result = []
    while i < 37:
        result = []
        filename = "/home/pi/Letters/Letter%d.txt" % i
        with open(filename, 'r') as csvfile:       
            read = csv.reader(csvfile, delimiter=',')
            for row in read:
                result.append(row)
        Templates[i-1, : ,:] = result
        i += 1   
    return Templates

Letters = np.array(["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P",
                    "Q","R","S","T","U","V","W","X","Y","Z","0","1","2","3","4","5","6","7","8","9"])

Templates = np.zeros((36,20,20))
Templates = DefTemps()

def Identify(Image):
    Guess = 'N/A'
    #Image = CameraInputRecognition.cameraGo()
    #Image = imread('pic.jpg')
    Image = Image/255
    Temp = np.zeros((20,20))
    scoreMax = 0
    i = 0
    for letter in Letters:             
        r = 0
        Temp = Templates[i, :, :]
        for r in range(0, 4):
            score = 0
            Temp = np.array(list(zip(*reversed(Temp))))
            for x in range(1, 19):
                for y in range(1, 19):
                    if Temp[x, y] == Image[x, y]:
                        score += 2
                    elif Temp[x+1, y] == Image[x, y]:
                        score += 1
                    elif Temp[x-1, y] == Image[x, y]:
                        score += 1    
                    elif Temp[x, y+1] == Image[x, y]:
                        score += 1    
                    elif Temp[x, y-1] == Image[x, y]:
                        score += 1                        
                    else:
                        score -= 0
                    y += 1
                x += 1            
            r += 1
            if score > scoreMax:
                scoreMax = score
                Guess = Letters[i]
            
        i += 1
       
    #confidence = scoreMax/4     
    print("Letter = " + str(Guess))
    return Guess
        

