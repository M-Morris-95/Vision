import csv
import numpy as np
import cv2

class Recognition:
    def __init__(self, size):
        self.Templates = np.zeros((144,size, size), dtype=bool)        
       
        i = 1
        j = 1
        result = []    
        
        while i < 37:
            result = []
            filename = "/home/pi/Letters/Letter%d.txt" % i
            with open(filename, 'r') as csvfile:       
                read = csv.reader(csvfile, delimiter=',')
                for row in read:
                    result.append(row)
                    
            for r in range(0, 4):
                result = np.array(list(zip(*reversed(result))))   
                self.Templates[j-1, : ,:] = result
                r += 1
                j += 1
                
            i += 1
            
            self.Letters = np.array(["A","B","C","D","E","F","G","H","I","J","K","L","M","N",
                                "O","P","Q","R","S","T","U","V","W","X","Y","Z","0","1",
                                "2","3","4","5","6","7","8","9"])               
        pass


    def Identify(self, Image, size):
        Guess = 'N/A'
        Guess1 = 'N/A'
        Guess2 = 'N/A'
        Image = Image/255
        #Image = imread('pic.jpg')
        #Image = Image < 127
        Temp = np.zeros((size,size))
        scoreMax = 0
        score1Max = 0
        score2Max = 0 
        r = 0
        while r < 4:
            i = 0
            while i < 36:         
                Temp = self.Templates[i+(r*36), :, :]
                score = 0
                score1 = 0
                score2 = 0
                                
                matrix = np.logical_xor(Temp,Image)
                score1 = np.sum(matrix)/4
                
                Temp = np.invert(Temp)
                Temp = Temp.astype(np.int)
                
                result = cv2.matchTemplate(
                    Image.astype(np.float32),
                    Temp.astype(np.float32),
                    cv2.TM_CCOEFF_NORMED)
                
                (minVal, maxVal, minLoc, maxLoc ) = cv2.minMaxLoc( result )
                score2 = maxVal*100
                
                score = (score1 * score2)/10000
                               
                
                if score1 > score1Max:
                    score1Max = score1
                    Guess1 = self.Letters[i]
                    
                if score2 > score2Max:
                    score2Max = score2
                    Guess2 = self.Letters[i]

                if score > scoreMax:
                    scoreMax = score
                    Guess = self.Letters[i]
                
                i += 1
            r += 1
           
        confidence = scoreMax/4     
        #print("Letter = " + str(Guess))
        #print("Confidence = " + str(confidence) + "%")
        print(Guess1, score1Max, Guess2, score2Max, Guess, scoreMax)
        #print(self.Letters[i], score1, score2, score)
        
        return Guess, confidence
        

