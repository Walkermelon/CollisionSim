import pygame
import math
import random
import time

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
WHITE = (255,255,255)
BLACK = (0,0,0)
GRAVITY = 5
FPS = 180
LAUNCH_FACTOR = 15
REFLECTIONS_MULTI = -0.5
DIVISIONS = 49
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
        self.DivisionsBelongTo = []
    
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


def ballCollisionDetection(ball1, ball2):
    xDis = abs(ball1.Cordinates[0]-ball2.Cordinates[0])
    yDis = abs(ball1.Cordinates[1]-ball2.Cordinates[1])
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

def chopVelocity(ball):
    factor = (1/(FPS-CHOPINTERVAL))
    if ball.Vector[0] <= gravity * factor and ball.Vector[0] >= -gravity * factor:
        ball.Vector[0] = 0
    if ball.Vector[1] <= gravity * factor and ball.Vector[1] >= -gravity * factor:
        ball.Vector[1] = 0

def addBallToQuad(ball, BallQuadrants):
    #print(newBall)
    divisions = DIVISIONS
    sections = SCREEN_WIDTH/divisions
    leftMostSection = int((ball.Cordinates[0]-ball.Radius)/sections)
    rightMostSection = int((ball.Cordinates[0]+ball.Radius)/sections)

    if rightMostSection == divisions: #fix getting extra section
        rightMostSection -= 1

    for i in range(leftMostSection, rightMostSection+1):
        BallQuadrants[i].append(ball)
        ball.DivisionsBelongTo.append(i)
    #print(f"{leftMostSection}  -  {rightMostSection} - {divisions}")
    

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

BallQuadrants =[]
for i in range(DIVISIONS):
    BallQuadrants.append(list())
AllBalls = []
newBall = None
clicking = False
clickingGravity = False
screen.fill(WHITE)
passes = 0
run = True
gravity = GRAVITY
passes = 0
startTime = time.time()

fillScreenWithBalls(12,10,1000,AllBalls)

while run:
    screen.fill(WHITE)
    #Keep FPS Fluent
    try:
        DT = 1/Clock.get_fps()
    except:
        DT = 1/FPS

    for ball in AllBalls:
        addBallToQuad(ball, BallQuadrants)
    
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
        newBall = None
        clicking = False

    #Turn off gravity
    if not pygame.mouse.get_pressed()[1]:
        clickingGravity = False
    elif not clickingGravity and gravity != 0 and pygame.mouse.get_pressed()[1]:
        gravity = 0
        clickingGravity = True
    elif not clickingGravity and gravity == 0 and pygame.mouse.get_pressed()[1]:
        gravity = GRAVITY
        clickingGravity = True
    

    #CHANG VELO PASS
   
    for ball in AllBalls:

        reflections = wallCollisionDetection(ball)
        ball.Vector[0] *= reflections[0]
        ball.Vector[1] *= reflections[1]

        if ball is not newBall:
            for divI in ball.DivisionsBelongTo:
                length = len(BallQuadrants[divI])
                for i in range(length):
                    if ball is not BallQuadrants[divI][i] and ballCollisionDetection(ball,BallQuadrants[divI][i]):

                        #Find correct collision
                        newVectors = collision(ball,BallQuadrants[divI][i])

                        #Update vectors
                        ball.updateVector(newVectors[0])
                        if BallQuadrants[divI][i] is not newBall:
                            BallQuadrants[divI][i].updateVector(newVectors[1])   
                    #Gravity
            ball.Vector[1] += gravity * (1/FPS)


        #Special Collison when ball is newBall
        else:
            #Ball Collision
            for divI in ball.DivisionsBelongTo:
                length = len(BallQuadrants[divI])
                for i in range(length):
                        if ball is not BallQuadrants[divI][i] and ballCollisionDetection(ball,BallQuadrants[divI][i]):

                            #Find correct collision
                            newVectors = collision(ball,BallQuadrants[divI][i])
                            BallQuadrants[divI][i].updateVector(newVectors[1])    


    #clear divisions for next round
    for divisions in BallQuadrants:
        divisions.clear()

    #CHANGE CORDS BASED ON NEW VELO PASS + DRAW
    for ball in AllBalls:
        #chopVelocity(ball)
        newCords = [ball.Cordinates[0] + ball.Vector[0], ball.Cordinates[1] + ball.Vector[1]]
        ball.updateCords(newCords)
        ball.drawCircle()
        ball.DivisionsBelongTo.clear()
    
       
    Clock.tick(FPS)
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    passes += 1
endTime = time.time()
print(f"pps: {passes/(endTime-startTime)}")

pygame.quit()
