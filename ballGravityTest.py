import pygame
import math
import random
import time

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
WHITE = (255,255,255)
BLACK = (0,0,0)
FPS = 180
LAUNCH_FACTOR = 0.1
REFLECTIONS_MULTI = -0.5
CHOPINTERVAL = 0


'''

BUGS:
-Balls glitching out border
-Once one ball stick, it makes any ball stick
    Happens because ball1 collides with ball2, then ball2 collides with ball3, bouncing it back owards ball1. Then ball1 doesnt exist to ball2 anymore bc already checked, so they stick.
-Ball that exists in mutiple quadrants will get bumped by another ball that exists in multiple quadrants, qaudrants many times

OPTIMIZATIONS:
-Calculate if collison is coming up before changing locations
to avoid going forward then going backward possibly
-Regional checks rather than global

IDEAS:
-Gravity
-Dynamic Launching


PLAN:
'''

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
Clock =  pygame.time.Clock()

class Ball:
    def __init__(self, Cordinates, Vector, Radius, Color):
        #Cordinates
        self.Cordinates = Cordinates
        #Vector
        self.Vector = Vector
        #Misc
        self.Radius = Radius
        self.Color = Color
    
    def updateCords(self, Cordinates):
        self.Cordinates = Cordinates

    def updateVector(self, Vector):
        self.Vector = Vector

    def updateRadius(self, Radius):
        self.Radius = Radius

    def drawCircle(self):
        pygame.draw.circle(screen, self.Color, self.Cordinates, self.Radius)

def collision(ball1, ball2):

    Vector1 = ball1.Vector
    Vector2 = ball2.Vector

    # Mass will be proportional to the radius
    Mass1 = ball1.Radius*2
    Mass2 = ball2.Radius*2

    # Normal vector between ball centers
    n = (ball2.Cordinates[0] - ball1.Cordinates[0], ball2.Cordinates[1] - ball1.Cordinates[1])
    nMagnitude = math.sqrt(n[0]**2 + n[1]**2)
    un = (n[0] / nMagnitude, n[1] / nMagnitude)  # Unit normal vector
    ut = (-un[1], un[0])  # Unit tangent vector (perpendicular to un)

    # Dot product for velocities along the normal and tangent directions
    v1n = un[0] * Vector1[0] + un[1] * Vector1[1]
    v1t = ut[0] * Vector1[0] + ut[1] * Vector1[1]
    v2n = un[0] * Vector2[0] + un[1] * Vector2[1]
    v2t = ut[0] * Vector2[0] + ut[1] * Vector2[1]

    # After collision (1D elastic collision equations)
    v1nPrime = (v1n * (Mass1 - Mass2) + 2 * Mass2 * v2n) / (Mass1 + Mass2)
    v2nPrime = (v2n * (Mass2 - Mass1) + 2 * Mass1 * v1n) / (Mass1 + Mass2)

    # Convert scalar normal and tangent velocities back to vectors
    v1nPrimeVec = [v1nPrime * un[0], v1nPrime * un[1]]
    v1tVec = [v1t * ut[0], v1t * ut[1]]
    v2nPrimeVec = [v2nPrime * un[0], v2nPrime * un[1]]
    v2tVec = [v2t * ut[0], v2t * ut[1]]

    # Final velocities
    newVector1 = [v1nPrimeVec[0] + v1tVec[0], v1nPrimeVec[1] + v1tVec[1]]
    newVector2 = [v2nPrimeVec[0] + v2tVec[0], v2nPrimeVec[1] + v2tVec[1]]
    

    # Fix overlap
    overlap = ball1.Radius + ball2.Radius - nMagnitude
    if overlap > 0:
        correction = overlap / 2
        ball1.Cordinates[0] -= correction * un[0]
        ball1.Cordinates[1] -= correction * un[1]
        ball2.Cordinates[0] += correction * un[0]
        ball2.Cordinates[1] += correction * un[1]

    return [newVector1, newVector2]

    
def ballCollisionDetection(ball1, ball2): #DETECTS BALL COLLISION
    xDis = ball1.Cordinates[0]-ball2.Cordinates[0]
    yDis = ball1.Cordinates[1]-ball2.Cordinates[1]
    rads = ball1.Radius + ball2.Radius
    return (xDis*xDis) + (yDis*yDis) <= (rads*rads) #Trying to avoid using sqrt

def wallCollisionDetection(ball):
    x = ball.Cordinates[0]
    y = ball.Cordinates[1]
    rad = ball.Radius
    reflection = [1, 1]  # (x, y)
    screen_width = SCREEN_WIDTH
    reflections_multi = REFLECTIONS_MULTI
    
    # x
    if x >= screen_width - rad:
        ball.Cordinates[0] = screen_width - rad
        reflection[0] = reflections_multi
    elif x <= rad:
        ball.Cordinates[0] = rad
        reflection[0] = reflections_multi

    # y
    if y >= screen_width - rad:
        ball.Cordinates[1] = screen_width - rad
        reflection[1] = reflections_multi
    elif y <= rad:
        ball.Cordinates[1] = rad
        reflection[1] = reflections_multi

    return reflection


def gravity(ball1, ball2):
    G = 1000
    # Compute distance between the two balls
    dx = ball2.Cordinates[0] - ball1.Cordinates[0]
    dy = ball2.Cordinates[1] - ball1.Cordinates[1]
    distance_squared = dx**2 + dy**2
    distance = math.sqrt(distance_squared) if distance_squared > 0 else 0.1  # Avoid division by zero
    
    # Compute force magnitude
    Mass1 = ball1.Radius * 2
    Mass2 = ball2.Radius * 2
    force = G * (Mass1 * Mass2) / distance_squared
        
    # Compute acceleration (F = ma -> a = F/m)
    ax1 = (force / Mass1) * (dx / distance)
    ay1 = (force / Mass1) * (dy / distance)
    ax2 = - (force / Mass2) * (dx / distance)  # Opposite reaction
    ay2 = - (force / Mass2) * (dy / distance)
        
    # Apply acceleration to velocity
    ball1.Vector[0] += ax1 * DT
    ball1.Vector[1] += ay1 * DT
    ball2.Vector[0] += ax2 * DT
    ball2.Vector[1] += ay2 * DT
    

def fillScreenWithBalls(radius, distance, amount, AllBalls):
    x = radius+distance
    y = radius+distance
    screen_width = SCREEN_WIDTH
    screen_height = SCREEN_HEIGHT
    for i in range(amount):
        RandomColor = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        AllBalls.append(Ball([x,y],[0,0],radius,RandomColor))
        if(x >= screen_width-radius-distance-1):
            x = radius+distance
            y += radius*2 + distance
        elif(y >= screen_height-radius-distance-1):
            break
        else:
            x += radius*2 + distance


AllBalls = []
newBall = None
clicking = False
screen.fill(WHITE)
passes = 0
run = True
passes = 0
startTime = time.time()

#fillScreenWithBalls(12,10,300,AllBalls)

while run:
    screen.fill(WHITE)
    #Keep FPS Fluent
    try:
        DT = 1/Clock.get_fps()
    except:
        DT = 1/FPS
    
    #MOUSE-BALL FUNCTIONALITY
    if not clicking and pygame.mouse.get_pressed()[0]:
        firstCords = pygame.mouse.get_pos()
        firstCordsConvertToList = [firstCords[0], firstCords[1]]
        Radius = 5
        RandomColor = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        newBall = Ball(firstCordsConvertToList,[0,0],Radius,RandomColor)
        clicking = True
        AllBalls.append(newBall)
    elif clicking and pygame.mouse.get_pressed()[0]:
        currCords = pygame.mouse.get_pos()
        currCordsConvertToList = [currCords[0], currCords[1]]
        newBall.updateCords(currCordsConvertToList)
        if(pygame.mouse.get_pressed()[2]):
            Radius += 0.5
            newBall.updateRadius(Radius)
    elif clicking and not pygame.mouse.get_pressed()[0]:
        finalCords = pygame.mouse.get_pos()
        newBall.Vector[0] = (finalCords[0]-currCords[0])*LAUNCH_FACTOR
        newBall.Vector[1] = (finalCords[1]-currCords[1])*LAUNCH_FACTOR
        newBall = None
        clicking = False
    

    #CHANG VELO PASS
   
    for i in range (len(AllBalls)):
        ball = AllBalls[i]
        reflections = wallCollisionDetection(ball)
        ball.Vector[0] *= reflections[0]
        ball.Vector[1] *= reflections[1]

        if ball is not newBall:
            for j in range(i+1,len(AllBalls)):
                currBall = AllBalls[j]
                gravity(ball,currBall)
                if ballCollisionDetection(ball,currBall):
                    #Find correct collision
                    newVectors = collision(ball,currBall)
                    #Update vectors
                    ball.updateVector(newVectors[0])
                    if currBall is not newBall:
                        currBall.updateVector(newVectors[1])   

        #Special Collison when ball is newBall
        else:
            for j in range(i+1,len(AllBalls)):
                currBall = AllBalls[j]
                gravity(ball,currBall)
                if ballCollisionDetection(ball,currBall):
                    #Find correct collision
                    newVectors = collision(ball,currBall)
                    #Update vectors
                    currBall.updateVector(newVectors[1])     


    #CHANGE CORDS BASED ON NEW VELO PASS + DRAW
    for ball in AllBalls:
        #chopVelocity(ball)
        newCords = [ball.Cordinates[0] + ball.Vector[0], ball.Cordinates[1] + ball.Vector[1]]
        ball.updateCords(newCords)
        ball.drawCircle()
    
       
    Clock.tick(FPS)
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    passes += 1
endTime = time.time()
print(f"pps: {passes/(endTime-startTime)}")

pygame.quit()
