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
        Image = Image/255
        #Image = imread('pic.jpg')
        #Image = Image < 127
        Temp = np.zeros((size,size))
        scoreMax = 0   
        r = 0
        while r < 4:
            i = 0
            while i < 36:         
                Temp = self.Templates[i+(r*36), :, :]       
                score = 0
                
                Temp = np.invert(Temp)
                
                matrix = np.logical_xor(Temp,Image)
                #matrix = np.invert(matrix)
                score1 = np.sum(matrix)
                
                
                result = cv2.matchTemplate(
                    Image.astype(np.float32),
                    Temp.astype(np.float32),
                    cv2.TM_CCOEFF)
                
                (minVal, maxVal, minLoc, maxLoc ) = cv2.minMaxLoc( result )
                score2 = maxVal
                
                score = score1 + score2

                if score > scoreMax:
                    scoreMax = score
                    Guess = self.Letters[i]
                
                i += 1
            r += 1
           
        confidence = scoreMax/4     
        #print("Letter = " + str(Guess))
        #print("Confidence = " + str(confidence) + "%")
        return Guess, confidence
        

