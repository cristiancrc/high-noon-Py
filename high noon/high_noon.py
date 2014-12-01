"""
High Noon 2012

version 1.0

My first python game, based on a z80 spectrum computer game from the `80
The original can be played here:
http://www.freevintagegames.com/SMSarcade/newarcade/spectrum/H/3/H/High%20Noon%201983Abbex%20Electronicsa.z80.php

Thanks to:
    Al Sweigart - the cat, the box images and his book http://inventwithpython.com/pygame/
    Flagamengine - the cowboy http://opengameart.org/content/cowboy-platform-and-isometric-sprite-sheet
    

written by Cristian Calmuschi
"""
import random, pygame, sys, webbrowser
from pygame.locals import *
pygame.init()

#dictionary
#                R    G    B
BLACK        = (  0,   0,   0)
WHITE        = (255, 255, 255)
RED          = (255,   0,   0)
GREEN        = (  0, 255,   0)
BLUE         = (  0,   0, 255)
YELLOW       = (255, 255,   0)
FUCHSIA      = (255,   0, 255)
CYAN         = (  0, 255, 255)
ORANGE       = (255, 128,   0)
PINK         = (255,   0, 128)
LIME         = (128, 255,   0)
LIGHTGREEN   = (  0, 255, 128)
SKYBLUE      = (  0, 128, 255)
DARKPURPLE   = (128,   0, 255)
GRAY         = (100, 100, 100)
NAVYBLUE     = ( 60,  60, 100)
REDT         = (255,   0,   0, 150)
BLUET        = (  0, 128, 255, 150)
NBLUE        = ( 60,  60, 100, 150)
SAND         = (255, 255, 200)
normal = 'normal'
hard = 'hard'
UP = 'up'
DOWN = 'down'
FIRE = 'fire'
FOCUS = 'focus'

#world settings
WINDOWWIDTH = 800 # size of window's width in pixels
WINDOWHEIGHT = 600 # size of windows' height in pixels
FPS = 60 # frames per second, the general speed of the program
FPSFOCUS = 20#speed during focus
BGCOLOR = SAND
DRAWCOLOR = BLACK
edgeClearance = 40 #distance from players to edge
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('High Noon')


#player settings
speedPlayer = 4 # player movement speed #should be set relative to bullet speed so dodge can happen in 1/2 screen(?)
speedBullet = 10 # bullet movement speed
animationDelay = 250 #time to display shooting
speedCarriage = 0.5
bulletWidth = 10#bullet rectangle width
bulletHeight = 2#bullet rectangle height
playerHealth = 4#how many bullets needed to score
bulletDamage = 1#should only modify playerHealth
AMMO = 6 # number of bullets available
playerFocus = 100#units of focus available
focusDrain = 10#units of focus lost per frame
focusRecharge = 0.2#units of focus regained per frame
difficulty = normal#default difficulty

#define keys
player1keys = {}
#player1keys = {UP:K_a}
player1keys[UP] = K_a
player1keys[DOWN] = K_z
player1keys[FIRE] = K_x
player1keys[FOCUS] = K_c

player2keys = {}
player2keys[UP] = K_UP
player2keys[DOWN] = K_DOWN
player2keys[FIRE] = K_RCTRL
player2keys[FOCUS] = K_SLASH

#font
BASICFONTSIZE = 20
SMALLFONTSIZE = 10
BIGFONT = pygame.font.Font('freesansbold.ttf', 50)
BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)
SMALLFONT = pygame.font.Font('freesansbold.ttf', SMALLFONTSIZE)


#load images and create collision rectangles
cowboy = pygame.image.load("cowboy.png")

imgTopClearance = 16#manually measured
imgTopToGun = 46-imgTopClearance#manually measured

imgPlayer1 = cowboy.subsurface(1423,8,116,121)
imgPlayer1fired = cowboy.subsurface(1664,8,116,121)
imgPlayer1hit = cowboy.subsurface(1664,506,116,121)
player1 = imgPlayer1.get_rect()
player1.height -= imgTopClearance#remove whitespace at top of the image
player1.left = edgeClearance#move away from the edge
player1.width = player1.width / 2#reduce the collision area
imgPlayer1left = player1.left - player1.width / 4#move image under the collision area

imgPlayer2 = cowboy.subsurface(1404,136,116,121)
imgPlayer2fired = cowboy.subsurface(1664,137,116,121)
imgPlayer2hit = cowboy.subsurface(1664,766,116,121)
player2 = imgPlayer2.get_rect()
player2.height -= imgTopClearance#remove whitespace at top of the image
player2.width = player2.width / 2#reduce the collision area
player2.right = WINDOWWIDTH - edgeClearance#move away from the edge
imgPlayer2left = player2.left - player2.width + player2.width / 4#move image under the collision area

imgCarriage = pygame.image.load('cat.png')
carriage = imgCarriage.get_rect()

imgObstacle1 = pygame.image.load('Wood_Block_Tall.png')
obstacle1 = imgObstacle1.get_rect()
obstacle1.top = edgeClearance
obstacle1.left = player1.right + obstacle1.width / 2 + edgeClearance
obstacle2 = imgObstacle1.get_rect()
obstacle2.top = WINDOWHEIGHT-obstacle2.height-player2.height
obstacle2.left = player2.left - obstacle2.width - obstacle2.width / 2 - edgeClearance

p1healthbar = pygame.Rect(player1.left, 0, player1.width, 15)
p2healthbar = pygame.Rect(player2.left, 0, player2.width, 15)

#debug draws aiming lines
shootingLineP1 = pygame.Rect(player1.right + 40, 0, WINDOWWIDTH, 2)
shootingLineP2 = pygame.Rect(0, 0, WINDOWWIDTH - player2.width - edgeClearance-40, 2)

#initialize variables
p1ammo = []
p2ammo = []
p1score = 0
p2score = 0
wanderPosition1 = 0
wanderPosition2 = 0
aicmd_fire1 = False
aicmd_fire2 = False

#blocky movement of carriage
pygame.time.set_timer(USEREVENT, 1000)

fpsClock = pygame.time.Clock()

#from Al Sweigart
def makeText(text, color, bgcolor, top, left, small = False, title = False):
    # create the Surface and Rect objects for some text.
    if(title):
        textSurf = BIGFONT.render(text, True, color, bgcolor)
    elif(small):
        textSurf = SMALLFONT.render(text, True, color, bgcolor)
    else:
        textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)
        
def terminate():
    pygame.quit()
    sys.exit()

def checkForQuit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    #for event in pygame.event.get(KEYUP): # get all the KEYUP events
    #    if event.key == K_ESCAPE:
    #        terminate() # terminate if the KEYUP event was for the Esc key
    #    pygame.event.post(event) # put the other KEYUP event objects back
        
#endfrom
def refill_ammo():#only called when both ammo lists are empty
    print("reload")
    #p1ammo = []
    #p2ammo = []
    for i in range(AMMO):
        p1ammo.append(pygame.Rect(10+10*i,10,bulletHeight,bulletWidth))
        p2ammo.append(pygame.Rect(WINDOWWIDTH-10-(10*i),10,bulletHeight,bulletWidth))
        
def main_menu():
    global player1keys, player2keys, difficulty
    GAMESPEED = 20
    bigDistance = 40#from top, including text size
    while True:
        checkForQuit()
        DISPLAYSURF.fill(BGCOLOR)
        #set text color based on current selection
        if(normal == difficulty):
            colorNormal = DRAWCOLOR
            colorHard = GRAY
        elif(hard == difficulty):
            colorNormal = GRAY
            colorHard = RED
        title_SURF, title_RECT = makeText("High Noon", DRAWCOLOR, BGCOLOR, WINDOWWIDTH /2 - 130, 40, False, True)
        start1_SURF, start1_RECT = makeText('1 - SINGLEPLAYER', DRAWCOLOR, BGCOLOR, WINDOWWIDTH /2 - 100, WINDOWHEIGHT / 2 - 120)
        start2_SURF, start2_RECT = makeText('2 - PLAYER VS PLAYER', DRAWCOLOR, BGCOLOR, WINDOWWIDTH /2 - 100, start1_RECT.top + bigDistance)
        redef_SURF , redef_RECT  = makeText('R - REDEFINE KEYS', DRAWCOLOR, BGCOLOR, WINDOWWIDTH /2 - 100, start2_RECT.top + bigDistance)#not yet
        demo_SURF, demo_RECT = makeText('D - DEMO', DRAWCOLOR, BGCOLOR, WINDOWWIDTH /2 - 100, redef_RECT.top+ bigDistance)
        quit_SURF , quit_RECT  = makeText('EXIT', DRAWCOLOR, BGCOLOR, WINDOWWIDTH /2 - 100, demo_RECT.top+ bigDistance)
        small = True
        difficulty_SURF , difficulty_RECT  = makeText('Difficulty:', DRAWCOLOR, BGCOLOR, WINDOWWIDTH /2 - 100, quit_RECT.top+ bigDistance, small)
        normal_SURF , normal_RECT  = makeText('normal', colorNormal, BGCOLOR, WINDOWWIDTH /2 - 30, quit_RECT.top+ bigDistance, small)
        hard_SURF , hard_RECT  = makeText('hard', colorHard, BGCOLOR, WINDOWWIDTH /2 + 30, quit_RECT.top+ bigDistance, small)
        pl1_text_SURF, pl1_text_RECT = makeText('Player 1', DRAWCOLOR, BGCOLOR, 20, 20, small)
        pl1_up_SURF, pl1_up_RECT = makeText(pygame.key.name(player1keys[UP])+' - up', DRAWCOLOR, BGCOLOR, 20, 40, small)
        pl1_down_SURF, pl1_down_RECT = makeText(pygame.key.name(player1keys[DOWN])+' - down', DRAWCOLOR, BGCOLOR, 20, 60, small)
        pl1_fire_SURF, pl1_fire_RECT = makeText(pygame.key.name(player1keys[FIRE])+' - fire', DRAWCOLOR, BGCOLOR, 20, 80, small)
        pl1_focus_SURF, pl1_focus_RECT = makeText(pygame.key.name(player1keys[FOCUS])+' - focus', DRAWCOLOR, BGCOLOR, 20, 100, small)
        pl2_text_SURF, pl2_text_RECT = makeText('Player 2', DRAWCOLOR, BGCOLOR, WINDOWWIDTH-100, 20, small)
        pl2_up_SURF, pl2_up_RECT = makeText(pygame.key.name(player2keys[UP])+' - up', DRAWCOLOR, BGCOLOR, WINDOWWIDTH-100, 40, small)
        pl2_down_SURF, pl2_down_RECT = makeText(pygame.key.name(player2keys[DOWN])+' - down', DRAWCOLOR, BGCOLOR, WINDOWWIDTH-100, 60, small)
        pl2_fire_SURF, pl2_fire_RECT = makeText(pygame.key.name(player2keys[FIRE])+' - fire', DRAWCOLOR, BGCOLOR, WINDOWWIDTH-100, 80, small)
        pl2_focus_SURF, pl2_focus_RECT = makeText(pygame.key.name(player2keys[FOCUS])+' - focus', DRAWCOLOR, BGCOLOR, WINDOWWIDTH-100, 100, small)
        madeby_SURF, madeby_RECT = makeText("remake by Cristian Calmuschi cristian.calmuschi@gmail.com", DRAWCOLOR, BGCOLOR, 50, WINDOWHEIGHT-120, small)
        thanks0_SURF, thanks0_RECT = makeText("thanks to:", DRAWCOLOR, BGCOLOR, 50, WINDOWHEIGHT-100, small)
        thanks1_SURF, thanks1_RECT = makeText("creators of pygame for...pygame http", DRAWCOLOR, BGCOLOR, 70, WINDOWHEIGHT-80, small)
        thanks2_SURF, thanks2_RECT = makeText("Al Sweigart for the book, the cat and the box images http", DRAWCOLOR, BGCOLOR, 70, WINDOWHEIGHT-60, small)
        thanks3_SURF, thanks3_RECT = makeText("Flagamengine for the cowboy http", DRAWCOLOR, BGCOLOR, 70, WINDOWHEIGHT-40, small)
        clone_SURF, clone_RECT = makeText("inspired by Abbex Electronics' 1983 High Noon http", DRAWCOLOR, BGCOLOR, 70, WINDOWHEIGHT-20, small)
        DISPLAYSURF.blit(title_SURF, title_RECT)
        DISPLAYSURF.blit(start1_SURF, start1_RECT)
        DISPLAYSURF.blit(start2_SURF, start2_RECT)
        DISPLAYSURF.blit(redef_SURF, redef_RECT)
        DISPLAYSURF.blit(demo_SURF, demo_RECT)
        DISPLAYSURF.blit(quit_SURF, quit_RECT)
        DISPLAYSURF.blit(difficulty_SURF, difficulty_RECT)
        DISPLAYSURF.blit(normal_SURF, normal_RECT)
        DISPLAYSURF.blit(hard_SURF, hard_RECT)
        DISPLAYSURF.blit(pl1_text_SURF, pl1_text_RECT)
        DISPLAYSURF.blit(pl1_up_SURF, pl1_up_RECT)
        DISPLAYSURF.blit(pl1_down_SURF, pl1_down_RECT)
        DISPLAYSURF.blit(pl1_fire_SURF, pl1_fire_RECT)
        DISPLAYSURF.blit(pl1_focus_SURF, pl1_focus_RECT)
        DISPLAYSURF.blit(pl2_text_SURF, pl2_text_RECT)
        DISPLAYSURF.blit(pl2_up_SURF, pl2_up_RECT)
        DISPLAYSURF.blit(pl2_down_SURF, pl2_down_RECT)
        DISPLAYSURF.blit(pl2_fire_SURF, pl2_fire_RECT)
        DISPLAYSURF.blit(pl2_focus_SURF, pl2_focus_RECT)
        DISPLAYSURF.blit(madeby_SURF, madeby_RECT)
        DISPLAYSURF.blit(thanks0_SURF, thanks0_RECT)
        DISPLAYSURF.blit(thanks1_SURF, thanks1_RECT)
        DISPLAYSURF.blit(thanks2_SURF, thanks2_RECT)
        DISPLAYSURF.blit(thanks3_SURF, thanks3_RECT)
        DISPLAYSURF.blit(clone_SURF, clone_RECT)
        for event in pygame.event.get(): # event handling loop
            if MOUSEBUTTONDOWN == event.type:
                if start1_RECT.collidepoint(event.pos):
                    main(1)
                elif start2_RECT.collidepoint(event.pos):
                    main(2)
                elif redef_RECT.collidepoint(event.pos):
                    redefine_keys()
                elif demo_RECT.collidepoint(event.pos):
                    main(0)                    
                elif quit_RECT.collidepoint(event.pos):
                    terminate()
            if KEYDOWN == event.type:
                if K_1 == event.key:
                    main(1)
                elif K_2 == event.key:
                    main(2)
                elif K_d == event.key:
                    main(0)                    
                elif K_r == event.key:
                    redefine_keys()                  
            elif MOUSEBUTTONUP == event.type:
                mousex, mousey = event.pos # syntactic sugar
                if pygame.Rect(hard_RECT).collidepoint(mousex, mousey):
                    difficulty = hard
                elif pygame.Rect(normal_RECT).collidepoint(mousex, mousey):
                    difficulty = normal
                elif pygame.Rect(difficulty_RECT).collidepoint(mousex, mousey):
                    difficulty = (normal if difficulty == hard else hard)
                elif pygame.Rect(thanks1_RECT).collidepoint(mousex, mousey):
                    webbrowser.open('http://www.pygame.org/news.html')
                elif pygame.Rect(thanks2_RECT).collidepoint(mousex, mousey):
                    webbrowser.open('http://inventwithpython.com/pygame/')
                elif pygame.Rect(thanks3_RECT).collidepoint(mousex, mousey):
                    webbrowser.open('http://opengameart.org/content/cowboy-platform-and-isometric-sprite-sheet') 
                elif pygame.Rect(clone_RECT).collidepoint(mousex, mousey):
                    webbrowser.open('http://www.freevintagegames.com/SMSarcade/newarcade/spectrum/H/3/H/High%20Noon%201983Abbex%20Electronicsa.z80.php') 
        pygame.display.update()
        fpsClock.tick(GAMESPEED)

def redefine_keys():
    global player1keys, player2keys
    player1keys = {}
    player2keys = {}
    GAMESPEED = 20
    bigDistance = 60
    while True:
        checkForQuit()
        DISPLAYSURF.fill(BGCOLOR)
        start1_SURF, start1_RECT = makeText('Player 1', DRAWCOLOR, BGCOLOR, WINDOWWIDTH /2 - 170, WINDOWHEIGHT / 2 - 150)
        pl1_up_SURF, pl1_up_RECT = makeText('up', BLACK, BGCOLOR, WINDOWWIDTH /2 - 170, start1_RECT.top + bigDistance)
        pl1_down_SURF, pl1_down_RECT = makeText('down', BLACK, BGCOLOR, WINDOWWIDTH /2 - 170, start1_RECT.top + bigDistance)
        pl1_fire_SURF, pl1_fire_RECT = makeText('fire', BLACK, BGCOLOR, WINDOWWIDTH /2 - 170, start1_RECT.top + bigDistance)
        pl1_focus_SURF, pl1_focus_RECT = makeText('focus', BLACK, BGCOLOR, WINDOWWIDTH /2 - 170, start1_RECT.top + bigDistance)

        start2_SURF, start2_RECT = makeText('Player 2', DRAWCOLOR, BGCOLOR, WINDOWWIDTH /2 - 170, WINDOWHEIGHT / 2 - 150)
        pl2_up_SURF, pl2_up_RECT = makeText('up', BLACK, BGCOLOR, WINDOWWIDTH /2 - 170, start2_RECT.top + bigDistance)
        pl2_down_SURF, pl2_down_RECT = makeText('down', BLACK, BGCOLOR, WINDOWWIDTH /2 - 170, start2_RECT.top + bigDistance)
        pl2_fire_SURF, pl2_fire_RECT = makeText('fire', BLACK, BGCOLOR, WINDOWWIDTH /2 - 170, start2_RECT.top + bigDistance)
        pl2_focus_SURF, pl2_focus_RECT = makeText('focus', BLACK, BGCOLOR, WINDOWWIDTH /2 - 170, start2_RECT.top + bigDistance)
        
        if(not(UP in player1keys)):
            DISPLAYSURF.blit(start1_SURF, start1_RECT)
            DISPLAYSURF.blit(pl1_up_SURF, pl1_up_RECT)
        elif(not(DOWN in player1keys)):
            DISPLAYSURF.blit(start1_SURF, start1_RECT)
            DISPLAYSURF.blit(pl1_down_SURF, pl1_down_RECT)
        elif(not(FIRE in player1keys)):
            DISPLAYSURF.blit(start1_SURF, start1_RECT)
            DISPLAYSURF.blit(pl1_fire_SURF, pl1_fire_RECT)
        elif(not(FOCUS in player1keys)):
            DISPLAYSURF.blit(start1_SURF, start1_RECT)
            DISPLAYSURF.blit(pl1_focus_SURF, pl1_focus_RECT)
        elif(not(UP in player2keys)):
            DISPLAYSURF.blit(start2_SURF, start2_RECT)
            DISPLAYSURF.blit(pl2_up_SURF, pl2_up_RECT)
        elif(not(DOWN in player2keys)):
            DISPLAYSURF.blit(start2_SURF, start2_RECT)
            DISPLAYSURF.blit(pl2_down_SURF, pl2_down_RECT)
        elif(not(FIRE in player2keys)):
            DISPLAYSURF.blit(start2_SURF, start2_RECT)
            DISPLAYSURF.blit(pl2_fire_SURF, pl2_fire_RECT)
        elif(not(FOCUS in player2keys)):
            DISPLAYSURF.blit(start2_SURF, start2_RECT)
            DISPLAYSURF.blit(pl2_focus_SURF, pl2_focus_RECT)

        for event in pygame.event.get(): # event handling loop
            if KEYDOWN == event.type and (K_ESCAPE != event.key):
                if(not(UP in player1keys)):
                    player1keys[UP] = (event.key)
                elif(not(DOWN in player1keys)):
                    player1keys[DOWN] = (event.key)
                elif(not(FIRE in player1keys)):
                    player1keys[FIRE] = (event.key)
                elif(not(FOCUS in player1keys)):
                    player1keys[FOCUS] = (event.key)
                elif(not(UP in player2keys)):
                    player2keys[UP] = (event.key)
                elif(not(DOWN in player2keys)):
                    player2keys[DOWN] = (event.key)
                elif(not(FIRE in player2keys)):
                    player2keys[FIRE] = (event.key)
                elif(not(FOCUS in player2keys)):
                    player2keys[FOCUS] = (event.key)    
        print(player1keys , player2keys)
        if(FOCUS in player2keys): main_menu()         
        pygame.display.update()
        fpsClock.tick(GAMESPEED)

def runAI(difficulty = normal, player = 2):#messy. only works for player2
    global aicmd_fire1, aicmd_fire2, wanderPosition1, wanderPosition2,p1fired, p2fired, p1ammoFired, p2ammoFired 
    #,randomMove1, randomMove2, randomMoveTarget1, randomMoveTarget2
    if(1 == player):
        player = player1
        enemy = player2
        playerShootingLine = shootingLineP1
        ammoFired = p2ammoFired
        enemyAmmo = p1ammo
    elif(2 == player):
        player = player2
        enemy = player1
        playerShootingLine = shootingLineP2
        ammoFired = p1ammoFired
        enemyAmmo = p2ammo
    
    #aicmd_fire1 = False
    aicmd_fire2 = False
    
    #positive tolerance is outside the collision box, negative reduces match
    seekPlayerToleranceMin = 30
    seekPlayerToleranceMax = 50
    seekCarriageToleranceMin = 80
    seekCarriageToleranceMax = 100
    fireTolerance = 10
    fireProbability = 98#if rand(0,100) higher then shoot, default 98

###movement
    if(hard == difficulty):
        if(ammoFired):#under attack
                ai_avoidBullets(player, ammoFired)
                ##ai_basicavoidBullets(player, ammoFired)
        else:
            if(0 == len(enemyAmmo)):#out of ammo
                ##ai_flee(player, enemy)#run to the other side of the screen
                ai_seek(player, carriage.centery, seekCarriageToleranceMin , seekCarriageToleranceMax)#hide behind the carriage
            else:
                ai_seek(player, enemy.centery, seekPlayerToleranceMin, seekPlayerToleranceMax)
                ##ai_follow(player, enemy,playerShootingLine)
                ##    randomMove2 = pygame.time.get_ticks()#randomMoveTarget1
                ##wanderPosition = ai_wander(player, wanderPosition2)
                1
    elif(normal == difficulty):
        if(ammoFired):#under attack
                ##ai_avoidBullets(player, ammoFired)#run to the other side of the screen
                ai_basicavoidBullets(player, ammoFired)
        else:
            if(0 == len(enemyAmmo)):#out of ammo
                ai_flee(player, enemy)
                ##ai_seek(player, carriage.centery, seekCarriageToleranceMin , seekCarriageToleranceMax)#hide behind the carriage
            else:
                ##ai_seek(player, enemy.centery, seekPlayerToleranceMin, seekPlayerToleranceMax)
                ai_follow(player, enemy, playerShootingLine)
                ##    randomMove2 = pygame.time.get_ticks()#randomMoveTarget1
                ##wanderPosition = ai_wander(player, wanderPosition2)
                1
###firing
    #ai_predict()#does not exist
    if(random.randint(0,100)>fireProbability):
        aicmd_fire2 = ai_fire(enemy, playerShootingLine, aicmd_fire2, fireTolerance)
    ai_shoot()#runAI must run after runAI2!

def runAI2(difficulty = normal, player = 1):#copy of runAI tailored for player1
    global aicmd_fire1, aicmd_fire2, wanderPosition1, wanderPosition2,p1fired, p2fired, p1ammoFired, p2ammoFired
    #, randomMove1, randomMove2, randomMoveTarget1, randomMoveTarget2
    if(1 == player):
        player = player1
        enemy = player2
        playerShootingLine = shootingLineP1
        ammoFired = p2ammoFired
        enemyAmmo = p1ammo
    elif(2 == player):
        player = player2
        enemy = player1
        playerShootingLine = shootingLineP2
        ammoFired = p1ammoFired
        enemyAmmo = p2ammo
    
    aicmd_fire1 = False
    #aicmd_fire2 = False
    
    #positive tolerance is outside the collision box, negative reduces match
    seekPlayerToleranceMin = 10
    seekPlayerToleranceMax = 10
    seekCarriageToleranceMin = 80
    seekCarriageToleranceMax = 100
    fireTolerance = 0
    fireProbability = 98#if rand(0,100) higher then shoot, default 98

###movement
    if(hard == difficulty):
        if(ammoFired):#under attack
                ai_avoidBullets(player, ammoFired)
                ##ai_basicavoidBullets(player, ammoFired)
        else:
            if(0 == len(enemyAmmo)):#out of ammo
                ##ai_flee(player, enemy)#run to the other side of the screen
                ai_seek(player, carriage.centery, seekCarriageToleranceMin , seekCarriageToleranceMax)#hide behind the carriage
            else:
                ai_seek(player, enemy.centery, seekPlayerToleranceMin, seekPlayerToleranceMax)
                ##ai_follow(player, enemy,playerShootingLine)
                ##    randomMove2 = pygame.time.get_ticks()#randomMoveTarget1
                ##wanderPosition = ai_wander(player, wanderPosition2)
                1
    elif(normal == difficulty):
        if(ammoFired):#under attack
                ##ai_avoidBullets(player, ammoFired)#run to the other side of the screen
                ai_basicavoidBullets(player, ammoFired)
        else:
            if(0 == len(enemyAmmo)):#out of ammo
                ai_flee(player, enemy)
                ##ai_seek(player, carriage.centery, seekCarriageToleranceMin , seekCarriageToleranceMax)#hide behind the carriage
            else:
                ##ai_seek(player, enemy.centery, seekPlayerToleranceMin, seekPlayerToleranceMax)
                ai_follow(player, enemy, playerShootingLine)
                ##    randomMove2 = pygame.time.get_ticks()#randomMoveTarget1
                ##wanderPosition = ai_wander(player, wanderPosition2)
                1
###firing
    #ai_predict()#does not exist
    if(random.randint(0,100)>fireProbability):
        aicmd_fire1 = ai_fire(enemy, playerShootingLine, aicmd_fire2, fireTolerance)

def ai_moveDown(player):
    #print("moveDown")
    player.top += speedPlayer2#higher number is down

def ai_moveUp(player):
    #print("moveUp")
    player.top -= speedPlayer2

def ai_basicavoidBullets(player, ammoFired):#easy
    #moves off bullet line as soon as bullet is detected, takes edge into account
    #does not take into account distance to bullet, firing two bullets one above half one below half generates a hit
    #print("--> simple bullet avoidance")
    #print("targets", ammoFired)
    for i in range(len(ammoFired)):
        if(ammoFired[i].centery <= player.bottom and ammoFired[i].centery >= player.top):
            #print("bottom:", player.bottom)
            #print("higher limit:", WINDOWHEIGHT)
            #print("top:",player.top)
            #print("lower limit:",0)
            #print("height:",player.height / 2)
            #print("avoiding ",ammoFired[i].centery)
            #decide direction
            if(ammoFired[i].centery >= player.top + player.height / 2):#lower half
                #print("lower half")
                #world margin
                if(ammoFired[i].centery <= player.height):#0 being worldy bottom (up)
                    #print("#no room to move up")
                    ai_moveDown(player)
                else:
                    ai_moveUp(player)
            elif(ammoFired[i].centery < player.top + player.height / 2):#higher half
                #print("higher half")
                if(ammoFired[i].centery >= WINDOWHEIGHT - player.height):
                    #print("#no room to move down")
                    ai_moveUp(player)
                else:
                    ai_moveDown(player)
            else: print("#######################rabbit")

def ai_avoidBullets(player, ammoFired):
    #dodges bullets at the last possible moment
    #shooting multiple bullets quickly will still go through
    #print("--> bullet avoidance")
    #print("targets", p1ammoFired)
    #player.Height-1 max distance
    #speedPlayer speed
    #t = d / v
    #speedBullet speed
    #d = v * t
    #avoids bullets at the last possible second, except when near margin when it doesn't work
    for i in range(len(ammoFired)):
        if(ammoFired[i].centery <= player.bottom and ammoFired[i].centery >= player.top):
            #print("bottom:", player.bottom)
            #print("higher limit:", WINDOWHEIGHT)
            #print("top:",player.top)
            #print("lower limit:",0)
            #print("height:",player.height / 2)
            onRight = onLeft = False
            #latest point when bullet can be dodged is on the right of the left player and vice versa
            if player.centerx > ammoFired[i].centerx:
                onRight = True
                goDown = player.centerx - int(player.width / 2) - int((ammoFired[i].centery - player.top) / speedPlayer * speedBullet) - 2 * bulletWidth
                goUp = player.centerx - int(player.width / 2) - int((player.bottom - ammoFired[i].centery) / speedPlayer * speedBullet)- 2 * bulletWidth
            else:
                onLeft = True
                goDown = player.centerx + int(player.width / 2) + int((ammoFired[i].centery - player.top) / speedPlayer * speedBullet) + 2 * bulletWidth
                goUp = player.centerx + int(player.width / 2) + int((player.bottom - ammoFired[i].centery) / speedPlayer * speedBullet)+ 2 * bulletWidth
                
            #pygame.draw.rect(DISPLAYSURF, RED, (goDown, ammoFired[i].centery, 2, 20),2)
            #pygame.draw.rect(DISPLAYSURF, SKYBLUE, (goUp, ammoFired[i].centery, 2, 20),2)
            #print("y avoiding ",ammoFired[i].centery)
            #decide direction
            if  ammoFired[i].centery <= player.height :#upper border
                #print("x dodging at ",goDown, " now at ", ammoFired[i].centerx)
                if(onRight and ammoFired[i].centerx >= goDown or onLeft and ammoFired[i].centerx <= goDown):
                    #print("border - moving down")
                    ai_moveDown(player)
            elif ammoFired[i].centery >= WINDOWHEIGHT - player.height :#lower border
                    #print("x dodging at ", goUp, " now at ", ammoFired[i].centerx)
                    if(onRight and ammoFired[i].centerx >= goUp or onLeft and ammoFired[i].centerx <= goUp):
                        #print("border - moving up")
                        ai_moveUp(player)                
            elif ammoFired[i].centery <= player.top + player.height / 2:#upper half
                    #print("x dodging at ",goDown, " now at ", ammoFired[i].centerx)
                    if(onRight and ammoFired[i].centerx >= goDown or onLeft and ammoFired[i].centerx <= goDown):
                        #print("moving down")
                        ai_moveDown(player)
            elif ammoFired[i].centery > player.top + player.height / 2:#lower half
                    #print("x dodging at ", goUp, " now at ", ammoFired[i].centerx)
                    if(onRight and ammoFired[i].centerx >= goUp or onLeft and ammoFired[i].centerx <= goUp):
                        #print("moving up")
                        ai_moveUp(player)
            else: print("#####################rabbit")#somehow no condition was valid, agent is sitting

def ai_seek(player, targetLine, toleranceMin = 1, toleranceMax = 1):
    #tolerance stops jerky movement, high tolerance 50+ makes moves in blocks
    #tolerance simulates some wander behaviour
    tolerance = random.randint(toleranceMin,toleranceMax)
    #print("--> seek from ",player.centery," to ", targetLine, " +-", tolerance )
    if int(player.centery/tolerance)*tolerance < int(targetLine/tolerance)*tolerance:
        ai_moveDown(player)
    elif int(player.centery/tolerance)*tolerance > int(targetLine/tolerance)*tolerance:
        ai_moveUp(player)

def ai_follow(player, enemy, playerShootingLine):
    tolerance = (random.randint(0, int(enemy.height)))
    #print("-->follow")
    if(playerShootingLine.centery > enemy.bottom - tolerance):
        ai_moveUp(player)
    if(playerShootingLine.centery < enemy.top + tolerance):
        ai_moveDown(player)

def ai_wander(player, wanderPosition):#not finished
    change = random.randint(-3,3)
    wanderPosition += change
    if(wanderPosition<-15): wanderPosition = -15
    elif(wanderPosition>15): wanderPosition = 15
    print("--> wander",wanderPosition)
    ai_seek(player, player.centery + wanderPosition)
    return (wanderPosition)

def ai_flee(player, enemy):
    #run away
    if(enemy.centery > WINDOWHEIGHT / 2):
        ai_seek(player, 0)
    else:
        ai_seek(player, WINDOWHEIGHT)

def ai_fire(enemy, playerShootingLine, playerFire, tolerance=0):
    if(playerShootingLine.centery < enemy.bottom + tolerance and playerShootingLine.centery > enemy.top - tolerance):
        #print('in crosshair')
        return True

def ai_shoot():
    global p1firedanim, p2firedanim
    if(aicmd_fire1):
        print("ai1 fire")
        if(len(p1ammo)>0):
            p1fired = pygame.time.get_ticks()
            p1firedanim = p1fired
            p1ammo[0].top = player1.top + 30 #bullet starts near gun
            p1ammo[0].left = player1.right + bulletWidth#bullet starts near gun
            p1ammo[0].width = bulletWidth#bullet is now horizontal
            p1ammo[0].height = bulletHeight#bullet is now horizontal
            p1ammoFired.append(p1ammo[0])
            #print (p1ammoFired)
            del p1ammo[0]
        else: print('p1 out of ammo')
    if(aicmd_fire2):
        print("ai2 fire")
        if(len(p2ammo)>0):
            p2fired = pygame.time.get_ticks()
            p2firedanim = p2fired
            p2ammo[0].top = player2.top + 30 #bullet starts near gun
            p2ammo[0].left = player2.left - bulletWidth#bullet starts near gun
            p2ammo[0].width = bulletWidth#bullet is now horizontal
            p2ammo[0].height = bulletHeight#bullet is now horizontal
            p2ammoFired.append(p2ammo[0])
            #print (p2ammoFired)
            del p2ammo[0]
        else: print('p2 out of ammo')   
        
    
def main(playerCount = 2):
    global p1score, p2score, p1ammo, p2ammo, BGCOLOR, DRAWCOLOR
    global speedPlayer1, speedPlayer2, aicmd_fire1, aicmd_fire2, p1fired, p2fired, p1ammoFired, p2ammoFired, randomMove1, randomMove2, randomMoveTarget1, randomMoveTarget2
    global p1firedanim, p2firedanim
    #print("score:",p1score, p2score)
    GAMESPEED = FPS
    speedPlayer1 = speedPlayer
    speedPlayer2 = speedPlayer
    #this might be improved
    if(1 == playerCount):print("starting right AI")
    if(0 == playerCount):print("starting both AIs")
    if(3 == playerCount):print("starting left AI")
    if(normal == difficulty):print(normal)
    if(hard == difficulty):print(hard)
    #reset player position
    #player1.top = WINDOWHEIGHT/2
    player1.top = random.randint(0, WINDOWHEIGHT)
    #player2.top = WINDOWHEIGHT/2
    player2.top = random.randint(0,WINDOWHEIGHT)
    #refill obstacles
    obstacle1pieces = []
    obstacle2pieces = []
    #stop rest of bullets
    p1ammoFired = []
    p2ammoFired = []
    #reset ammo
    p1ammo = []
    p2ammo = []
    #reset carriage
    carriage.left = int((WINDOWWIDTH - imgCarriage.get_width())/2)
    carriage.top = WINDOWHEIGHT
    imgCarriagey = carriage.top#required for the image to gracefully exit the screen
    imgCarriagex = carriage.left#required for the image to gracefully exit the screen
    
    #reset match variables
    p1fired = False#when p1 fired previous time
    p2fired = False#when p2 fired previous time
    p1firedanim = False#when p1 fired, used for animation
    p2firedanim = False#when p2 fired, used for animation
    p1hit = False#bool for player hit
    p2hit = False#bool for player hit
    p1won = False#bool for extinguishing other player's health
    p2won = False#bool for extinguishing other player's health
    p1focusstate = False#deactivates focus
    p2focusstate = False
    p1focus = playerFocus
    p2focus = playerFocus
    p1focusDrain = focusDrain
    p2focusDrain = focusDrain
    p1focusRecharge = focusRecharge
    p2focusRecharge = focusRecharge
    p1health = p2health = playerHealth
    #randomMove1 = False#when this was triggered
    #randomMove2 = False
    #randomMoveTarget1 = 0
    #randomMoveTarget2 = 0
        
    while True: # the main game loop
        DISPLAYSURF.fill(BGCOLOR)#called here because ai_avoidBullets draws debug rectangles
        #check game state
        if p1health <= 0:
            p2won = True
            p2score += 1
        if p2health <= 0:
            p1won = True
            p1score += 1
        
        if(p1won or p2won): pygame.time.delay(1000); main(playerCount)
                
        if(0 == len(p1ammo) and 0 == len(p2ammo)):
            refill_ammo()

        #run AI
        if(1 == playerCount):
            runAI(difficulty)
        elif(0 == playerCount):
            runAI2(normal)
            runAI(difficulty)
        elif(3 == playerCount):
            runAI2(difficulty)#only AI on left player
            
        #animations
        if(pygame.time.get_ticks() > p1firedanim + animationDelay): p1firedanim = False;
        if(pygame.time.get_ticks() > p2firedanim + animationDelay): p2firedanim = False
        if(pygame.time.get_ticks() > p1hit + animationDelay): p1hit = False
        if(pygame.time.get_ticks() > p2hit + animationDelay): p2hit = False

        key=pygame.key.get_pressed()
        #movement
        if key[player1keys[UP]]:         player1.top -= speedPlayer1
        if key[player1keys[DOWN]]:       player1.top += speedPlayer1
        if key[player2keys[UP]]:         player2.top -= speedPlayer2
        if key[player2keys[DOWN]]:       player2.top += speedPlayer2
        if key[K_r] and key[K_LSHIFT]:     refill_ammo()#temp
    
        #SMOOTH move carriage
        imgCarriagey -= speedCarriage
        carriage.top = imgCarriagey
        
        #movement limits
        if(player1.top < 0): player1.top = 0
        if(player1.top > (WINDOWHEIGHT - player1.height)): player1.top = (WINDOWHEIGHT - player1.height)
        if(player2.top < 0): player2.top = 0
        if(player2.top > (WINDOWHEIGHT - player2.height)): player2.top = (WINDOWHEIGHT - player2.height)
        if(carriage.top < 0 - carriage.height): imgCarriagey = WINDOWHEIGHT
        
        #other rectangles
        shootingLineP1.top = player1.top + imgTopToGun
        shootingLineP2.top = player2.top + imgTopToGun
        p1healthbar.top = player1.top-20#manually positioned
        p2healthbar.top = player2.top-20

        #focus state
        if(p1focusstate):
            p1focus -= p1focusDrain
            if(p1focus <= 0):
                p1focusstate = False
        else: 
            if(p1focus < playerFocus):
                p1focus +=p1focusRecharge
        if(p2focusstate):
            p2focus -= p2focusDrain
            if(p2focus <= 0):
                p2focusstate = False
        else: 
            if(p2focus < playerFocus):
                p2focus +=p2focusRecharge        
        
        
        #if key[pygame.K_q]:
        ###deal with keypresses
        for event in pygame.event.get():
            if QUIT == event.type:
                terminate()
            if KEYDOWN == event.type and K_ESCAPE == event.key:
                main_menu()
            #BLOCK move carriage
            #if(USERVENT == event.type):
            #    carriage.top -= carriage.height/2 
            ##firing
            if KEYDOWN == event.type and player1keys[FIRE] == event.key:
                if(len(p1ammo)>0):
                    p1fired = pygame.time.get_ticks()
                    p1firedanim = p1fired
                    p1ammo[0].top = player1.top + 30 #bullet starts near gun
                    p1ammo[0].left = player1.right + bulletWidth #bullet starts near gun
                    p1ammo[0].width = bulletWidth#bullet is now horizontal
                    p1ammo[0].height = bulletHeight#bullet is now horizontal
                    p1ammoFired.append(p1ammo[0])
                    #print (p1ammoFired)
                    del p1ammo[0]
                else: print('p1 out of ammo')
            if KEYDOWN == event.type and player2keys[FIRE] == event.key:
                if(len(p2ammo)>0):
                    p2fired = pygame.time.get_ticks()
                    p2firedanim = p2fired
                    p2ammo[0].top = player2.top + 30
                    p2ammo[0].left = player2.left - bulletWidth
                    p2ammo[0].width = bulletWidth#bullet is now horizontal
                    p2ammo[0].height = bulletHeight#bullet is now horizontal
                    p2ammoFired.append(p2ammo[0])
                    del p2ammo[0]
                else: print('p2 out of ammo')
            ##manage focus#messy
            #p1
            if KEYDOWN == event.type and player1keys[FOCUS] == event.key and p1focus>=p1focusDrain:
                print('starting p1 focus')
                p1focusstate = True
                GAMESPEED = FPSFOCUS
                BGCOLOR = BLACK
                DRAWCOLOR = GREEN
                speedPlayer1 = speedPlayer1 * FPS / FPSFOCUS 
            if KEYUP == event.type and player1keys[FOCUS] == event.key or p1focus<=5:
                print('stopping p1 focus')
                GAMESPEED = FPS
                BGCOLOR = SAND
                DRAWCOLOR = BLACK
                speedPlayer1 = speedPlayer
                p1focusstate = False
            #p2
            if KEYDOWN == event.type and player2keys[FOCUS] == event.key and p2focus>=p2focusDrain:
                print('starting p2 focus')
                p2focusstate = True
                GAMESPEED = FPSFOCUS
                BGCOLOR = BLACK
                DRAWCOLOR = GREEN
                speedPlayer2 = speedPlayer2 * FPS / FPSFOCUS 
            if KEYUP == event.type and player2keys[FOCUS] == event.key or p2focus<=5:
                print('stopping p2 focus')
                GAMESPEED = FPS
                BGCOLOR = SAND
                DRAWCOLOR = BLACK
                speedPlayer2 = speedPlayer
                p2focusstate = False
                
        ###advance bullets and collision detection
        #p1
        for i in range(len(p1ammoFired)):
            if p1ammoFired[i].colliderect(carriage):
                del p1ammoFired[i]
                break
            if p1ammoFired[i].colliderect(obstacle1):
                if -1 == p1ammoFired[i].collidelist(obstacle1pieces):
                    #perfect collision detection depends on speedBullet, this is trial and error for EACH obstacle
                    obstacle1pieces.append(pygame.Rect(p1ammoFired[i].left,p1ammoFired[i].top-obstacle1.width/2/2,obstacle1.width/2+5, obstacle1.width/2))
                    del p1ammoFired[i]
                    break
            if p1ammoFired[i].colliderect(obstacle2):
                if -1 == p1ammoFired[i].collidelist(obstacle2pieces) : 
                    obstacle2pieces.append(pygame.Rect(p1ammoFired[i].left-4,p1ammoFired[i].top-obstacle2.width/2/2,obstacle2.width/2+15, obstacle2.width/2))
                    del p1ammoFired[i]
                    break    
            if p1ammoFired[i].colliderect(player2):
                p2health -= bulletDamage
                p2hit = pygame.time.get_ticks()
                del p1ammoFired[i]
                break
            #move
            if(p1ammoFired[i].left<WINDOWWIDTH):
                p1ammoFired[i].left += speedBullet
            if(p1ammoFired[i].left >=WINDOWWIDTH):
                del p1ammoFired[i]
                break
                #p1ammoFired[i].left = WINDOWWIDTH - p1ammoFired[i].width #bullet stays in screen, useful for arrows
        #p2
        for i in range(len(p2ammoFired)):
            if p2ammoFired[i].colliderect(carriage):
                del p2ammoFired[i]
                break
            if p2ammoFired[i].colliderect(obstacle1):
                if -1 == p2ammoFired[i].collidelist(obstacle1pieces): 
                    obstacle1pieces.append(pygame.Rect(p2ammoFired[i].left-obstacle2.width/2,p2ammoFired[i].top-obstacle2.width/2/2,obstacle2.width/2+15, obstacle2.width/2))
                    del p2ammoFired[i]
                    break
            if p2ammoFired[i].colliderect(obstacle2):
                if -1 == p2ammoFired[i].collidelist(obstacle2pieces): 
                    obstacle2pieces.append(pygame.Rect(p2ammoFired[i].left-obstacle2.width/2+5,p2ammoFired[i].top-obstacle2.width/2/2,obstacle2.width/2+5, obstacle2.width/2))
                    del p2ammoFired[i]
                    break        
            if p2ammoFired[i].colliderect(player1):
                p1health -= bulletDamage
                p1hit = pygame.time.get_ticks()
                del p2ammoFired[i]
                break
            #move
            if(p2ammoFired[i].left>0-bulletWidth):#0 to stay in screen
                p2ammoFired[i].left -= speedBullet
            if(p2ammoFired[i].left<=0-bulletWidth):#0 to stay in screen
                del p2ammoFired[i]
                break
                #p2ammoFired[i].left = 0 # bullet stays in screen
        
        ####draw frame
        #DISPLAYSURF.fill(BGCOLOR)#called at the beginning of the loop because of ai_avoidBullets debug

        #draw scene
        DISPLAYSURF.blit(imgCarriage, (imgCarriagex, imgCarriagey))
        DISPLAYSURF.blit(imgObstacle1, obstacle1)
        DISPLAYSURF.blit(imgObstacle1, obstacle2)
        
        #draw broken pieces
        for i in range(len(obstacle1pieces)):
            pygame.draw.rect(DISPLAYSURF, BGCOLOR, obstacle1pieces[i])
        for i in range(len(obstacle2pieces)):
            pygame.draw.rect(DISPLAYSURF, BGCOLOR, obstacle2pieces[i])
        
        #draw bullets
        for i in range(len(p1ammo)):
            pygame.draw.rect(DISPLAYSURF, DRAWCOLOR, p1ammo[i])    
        for i in range(len(p1ammoFired)):
            pygame.draw.rect(DISPLAYSURF, DRAWCOLOR, p1ammoFired[i])
        for i in range(len(p2ammo)):
            pygame.draw.rect(DISPLAYSURF, DRAWCOLOR, p2ammo[i])    
        for i in range(len(p2ammoFired)):
            pygame.draw.rect(DISPLAYSURF, DRAWCOLOR, p2ammoFired[i])
            
        #draw health bar
        if(playerHealth != bulletDamage):
            DISPLAYSURF.fill(RED, (p1healthbar.left, p1healthbar.top, (p1health * 100 / playerHealth * p1healthbar.width / 100), p1healthbar.height ))
            pygame.draw.rect(DISPLAYSURF, DRAWCOLOR, p1healthbar,2)
            DISPLAYSURF.fill(RED, (p2healthbar.left, p2healthbar.top, (p2health* 100 / playerHealth * p2healthbar.width / 100), p2healthbar.height ))
            pygame.draw.rect(DISPLAYSURF, DRAWCOLOR, p2healthbar,2)
        if(p1focusstate):
            DISPLAYSURF.fill(DRAWCOLOR, (edgeClearance * 2, WINDOWHEIGHT - edgeClearance, p1focus, 5))
            pygame.draw.rect(DISPLAYSURF, WHITE, (edgeClearance * 2, WINDOWHEIGHT - edgeClearance, 100, 5),2)
        if(p2focusstate):
            DISPLAYSURF.fill(DRAWCOLOR, (WINDOWWIDTH - edgeClearance * 2 - 100, WINDOWHEIGHT - edgeClearance, p2focus, 5))
            pygame.draw.rect(DISPLAYSURF, WHITE, (WINDOWWIDTH - edgeClearance * 2 - 100, WINDOWHEIGHT - edgeClearance, 100, 5),2)            

        #draw score
        score1_SURF, score1_RECT = makeText(str(p1score), DRAWCOLOR, BGCOLOR, WINDOWWIDTH /2 - 100, 10, True)
        DISPLAYSURF.blit(score1_SURF, score1_RECT)
        score2_SURF, score2_RECT = makeText(str(p2score), DRAWCOLOR, BGCOLOR, WINDOWWIDTH /2 + 100, 10, True)
        DISPLAYSURF.blit(score2_SURF, score2_RECT)        
        
        #draw players
        if p1hit:
            DISPLAYSURF.blit(imgPlayer1hit, (imgPlayer1left, player1.top-imgTopClearance))
        elif p1firedanim:
            DISPLAYSURF.blit(imgPlayer1fired, (imgPlayer1left, player1.top-imgTopClearance))
        else:
            DISPLAYSURF.blit(imgPlayer1, (imgPlayer1left, player1.top-imgTopClearance))
        if p2hit:
            DISPLAYSURF.blit(imgPlayer2hit, (imgPlayer2left, player2.top-imgTopClearance))
        elif p2firedanim:
            DISPLAYSURF.blit(imgPlayer2fired, (imgPlayer2left, player2.top-imgTopClearance))
        else:
            DISPLAYSURF.blit(imgPlayer2, (imgPlayer2left, player2.top-imgTopClearance))
        
        #debug draw collision rectangles
        #ALPHASURF = DISPLAYSURF.convert_alpha()
        #pygame.draw.rect(ALPHASURF, NBLUE, carriage)
        #pygame.draw.rect(ALPHASURF, REDT, player1)
        #pygame.draw.rect(ALPHASURF, BLUET, player2)
        #pygame.draw.rect(ALPHASURF, NBLUE, obstacle1)
        #pygame.draw.rect(ALPHASURF, NBLUE, obstacle2)
        #pygame.draw.rect(ALPHASURF, REDT, shootingLineP1)
        #pygame.draw.rect(ALPHASURF, BLUET, shootingLineP2)
        #DISPLAYSURF.blit(ALPHASURF,(0,0))
        
        pygame.display.update()
        fpsClock.tick(GAMESPEED)
        
if __name__ == '__main__':
    main_menu()                
    #main(0)

