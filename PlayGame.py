"""
PlayGame.py created by Christopher Cleary
MY FIRST VIDEO GAME! (QUEST)

--Background tile images and game sounds from
    http://opengameart.org/
    
--All game music from
    http://www.vgmusic.com/
    "Starlight Road" (GameMenu) - from Super Mario RPG (SNES)
    "Mushroom Way" (MainGameMusic) - from Super Mario RPG (SNES)
    "Fairy Song" (GameOverMusic) - from Legend of Zelda: link to the past (SNES)
    
--All other artwork by Christopher Cleary
"""
import pygame, sys, random, cPickle, time
from RPGEngine import *

class GetInput(InputManager):
    pass
class NewPlayer(Player):
    pass
class Enemy(Enemy):
    pass
class Background(Background):
    pass
class GameObjects(GameObjects):
    pass

"""INITIALIZE ALL GAME COMPONENTS"""
pygame.init()

pygame.mouse.set_visible(False)
FPS = 60 # frames per second setting
fpsClock = pygame.time.Clock()
animPOS = 0
delay = 0
gameFont = pygame.font.Font(None, 32)
WHITE = (255,255,255)
BLACK = (0,0,0)
LEVELUP = gameFont.render("LEVEL UP", True, (255,255,0))

# set up the window to fullscreen, and initialize game
winWidth = 640
camX = 320
winHeight = 480
camY = 4480
camRect = pygame.Rect(0,0,640,480)
DISPLAY = pygame.display.set_mode((winWidth, winHeight))
numJoysticks = pygame.joystick.get_count()
#initialize our input manager to handle joysticks or keyboard input.
inputManager = GetInput()
if numJoysticks > 0:
    inputManager.load_config(DISPLAY)

#initialize the background for playering
background = Background(320,4480)
background.load_tiles(["tiles\grass.png", "tiles\stone.png", "tiles\water.png"])

#initialize game sounds
coinSound = pygame.mixer.Sound("sounds\coin.wav")
swordSound = pygame.mixer.Sound("sounds\sword.wav")
potionSound = pygame.mixer.Sound("sounds\potion.wav")
potionIcon = pygame.image.load("images\potion.png")
coinIcon = pygame.image.load("images\coin.png")

#initialize a new player and some other game objects
player = NewPlayer(640, 400, 1, 100, 10, 10,5,5,5,20,0,0,"DOWN") # create an instance of the player object
player.load_images("up", ["images\Player\playerUP.png"])
player.load_images("attack-up", ["images\Player\playerATTACKUP.png"])
player.load_images("down", ["images\Player\playerDOWN.png"])
player.load_images("attack-down", ["images\Player\playerATTACKDOWN.png"])
player.load_images("horizontal", ["images\Player\playerHOR.png"])
player.load_images("attack-horizontal", ["images\Player\playerHORATTACK.png"])
player.load_images("dead", ["images\Player\playerDEAD.png"])
spell = pygame.image.load("images\Heal.png")
player.spellImages.append(spell)
spell = pygame.image.load("images\Fireball.png")
player.spellImages.append(spell)
spell = pygame.image.load("images\Frost.png")
player.spellImages.append(spell)
spell = pygame.image.load("images\Oblivion.png")
player.spellImages.append(spell)
player.animate(0)
menuImage = pygame.image.load("images\MainMenu.png")
go1Image = pygame.image.load("images\gameover1.png")
go2Image = pygame.image.load("images\gameover2.png")
stores = []
storeInv = {"Oblivion": 1, "Frost": 1, "potion": 500}
enemies = []
bounds = []
deathtraps = []
items = []

"""***************"""
"""GAME FUNCTIONS:"""
"""***************"""

def mainGame():
    global animPOS, delay
    # our game needs background music...hello
    pygame.mixer.music.load("music\GameMusic.mp3") # load the file to the music mixer
    pygame.mixer.music.play(-1,0.0) # play the file loaded in the mixer
                                # (-1 means loop forever, starting at 0.0 seconds)
    while True: # the main game loop
        delay += 1
        if delay == 11:
            player.interact = False
            player.isAttacking = False
            if player.curSpell == "Heal": player.isCasting = False
            player.curMP += player.level
            if player.curMP > player.totMP: player.curMP = player.totMP
            delay = 0
            animPOS = 0

        # Handle each event during the game loop
        for event in inputManager.getEvents():
            if event.key == "A" and event.down:
                player.isAttacking = True
            if event.key == "B" and event.down:
                player.interact = True
            if event.key == "X" and event.down:
                usePotion()
            if event.key == "Y" and event.down:
                if player.curMP > 0 and player.curMP >= player.mpCost:
                    player.isCasting = True
                    player.spellDirection = player.direction
                    player.spellX = player.x
                    player.spellY = player.y
                    player.spellRect.center = (player.spellX, player.spellY)
                    player.curMP -= player.mpCost
                    if player.curMP < 0:
                        player.curMP = 0
            if event.key == "L" and event.down:
                showMagicMenu()
            if event.key == "start" and event.down:
                showGameMenu()
                
        # handle inputs and move accordingly    
        if inputManager.isPressed("up"):
            moveUp()
        if inputManager.isPressed("down"):
            moveDown()
        if inputManager.isPressed("left"):
            moveLeft()
        if inputManager.isPressed("right"):
            moveRight()

        # move the cast spell, if any have been
        if player.isCasting and not player.curSpell == "Heal":
            if player.spellDirection == "UP":
                player.spellY -= 20
            if player.spellDirection == "DOWN":
                player.spellY += 20
            if player.spellDirection == "RIGHT":
                player.spellX += 20
            if player.spellDirection == "LEFT":
                player.spellX -= 20
        elif player.isCasting and player.curSpell == "Heal":
            player.spellDirection = "UP"
            player.spellY -= 10
            player.curHP += (player.wisdom + player.level)
            
        #move the enemies around the game
        for enemy in enemies:
            enemy.determine_motion()
            enemy.detect_player(player.charRect, player.charRect)
            enemy.animate(0)
            
        # animate player and enemies after each move
        if player.isAttacking:
            player.attack(0)
        else:
            player.animate(0) # change the player image
        
        # detect collisions....
        detectCollisions()

        # check for enemy deaths and see if the player died
        for enemy in enemies:
            if enemy.is_dead():
                dropCoins(enemy.x, enemy.y, enemy.gold, enemy.exp)                
                enemies.remove(enemy)
                newEnemy()
        if player.is_dead():
            player.set_image(player.animDEAD[0])

        #draw the background
        background.render(DISPLAY)
        #render the game objects
        for bound in bounds:
            if bound.objRect.colliderect(camRect):
                bound.render(DISPLAY)
        for deathtrap in deathtraps:
            if deathtrap.objRect.colliderect(camRect):
                deathtrap.render(DISPLAY)
        for item in items:
            if item.objRect.colliderect(camRect):
                item.render(DISPLAY)
        for store in stores:
            if store.objRect.colliderect(camRect):
                store.render(DISPLAY)
                
        #render the players sprite    
        player.render(DISPLAY)  # render the sprites to the display 
        for enemy in enemies:
            if enemy.charRect.colliderect(camRect):
                enemy.render(DISPLAY)
        if not player.spellRect.colliderect(camRect):
            player.isCasting = False 
        drawHUD()
        if player.levelUp:
            DISPLAY.blit(LEVELUP, (590, 240))
        pygame.display.update() # update the screen
        animPOS += 1
        if player.is_dead():
           gameOver()
        fpsClock.tick(FPS) # wait...

#mainMenu displays the opening menu and handles new game, load, or exit.
def mainMenu():
    global camX, camY
    menuPos = 2
    pygame.mixer.music.load("music\MenuMusic.mp3") # load the file to the music mixer
    pygame.mixer.music.play(-1,0.0) # play the file loaded in the mixer
    while True:
        numJoysticks = pygame.joystick.get_count()
        DISPLAY.fill((0,0,0))
        #limit the menu position    
        if numJoysticks == 0:
            if menuPos > 29: menuPos = 29
        else:
            if menuPos > 39: menuPos = 39
        if menuPos < 0: menuPos = 0
        #setup the menu text according to menuPos
        if menuPos > -1 and menuPos < 10:
            text1 = gameFont.render("> New Game", True, WHITE)
        else:
            text1 = gameFont.render("  New Game", True, WHITE)
        if menuPos > 9 and menuPos < 20:
            text2 = gameFont.render("> Load Game", True, WHITE)
        else:
            text2 = gameFont.render("  Load Game", True, WHITE)
        if menuPos > 19 and menuPos < 30:
            text3 = gameFont.render("> Quit Game", True, WHITE)
        else:
            text3 = gameFont.render("  Quit Game", True, WHITE)
        if numJoysticks > 0:
            if menuPos > 29:
                text4 = gameFont.render("> Joystick Configuration", True, WHITE)
            else:
                text4 = gameFont.render("  Joystick Configuration", True, WHITE)
        else:
            text4 = gameFont.render("", False, WHITE)
        #setup the menu items for display
        text1Rect = text1.get_rect()
        text2Rect = text2.get_rect()
        text3Rect = text3.get_rect()
        text4Rect = text4.get_rect()
        text1Rect.center = (640, 400)
        text2Rect.center = (640, 475)
        text3Rect.center = (640, 550)
        text4Rect.center = (640, 625)
        imageRect = menuImage.get_rect()
        imageRect.center = (640, 200)
        #draw the text to the screen
        DISPLAY.blit(menuImage, imageRect)
        DISPLAY.blit(text1, text1Rect)
        DISPLAY.blit(text2, text2Rect)
        DISPLAY.blit(text3, text3Rect)
        DISPLAY.blit(text4, text4Rect)
        pygame.display.update()
        waiting = True
        while waiting:
            #handle keyboard/joystick input
            for event in inputManager.getEvents():
                if event.key == "B" and event.down:
                    if menuPos > -1 and menuPos < 10:
                        # start a new game
                        player.__init__(640, 400, 1, 100, 10, 10,5,5,5,20,0,0,"DOWN")
                        player.load_images("up", ["images\Player\playerUP.png"])
                        player.load_images("attack-up", ["images\Player\playerATTACKUP.png"])
                        player.load_images("down", ["images\Player\playerDOWN.png"])
                        player.load_images("attack-down", ["images\Player\playerATTACKDOWN.png"])
                        player.load_images("horizontal", ["images\Player\playerHOR.png"])
                        player.load_images("attack-horizontal", ["images\Player\playerHORATTACK.png"])
                        player.load_images("dead", ["images\Player\playerDEAD.png"])
                        spell = pygame.image.load("images\Heal.png")
                        player.spellImages.append(spell)
                        spell = pygame.image.load("images\Fireball.png")
                        player.spellImages.append(spell)
                        spell = pygame.image.load("images\Frost.png")
                        player.spellImages.append(spell)
                        spell = pygame.image.load("images\Oblivion.png")
                        player.spellImages.append(spell)
                        player.animate(0)
                        background.__init__(320,4480)
                        background.load_tiles(["tiles\grass.png", "tiles\stone.png", "tiles\water.png"])
                        camX = 320
                        camY = 4480
                        newGame()
                        mainGame()
                    if menuPos > 9 and menuPos < 20:
                        loadGame()
                    if menuPos > 19 and menuPos < 30:
                        terminate()
                    if menuPos > 29:
                        inputManager.joystickConfig = {}
                        yPos = 200
                        isConfig = False
                        index = 0
                        DISPLAY.fill((0,0,0))
                        text = gameFont.render("GET READY! DON'T PRESS ANY BUTTONS YET!!! WAIT 3 SECONDS!", True, (255,255,255))
                        textRect = text.get_rect()
                        textRect.center = (400, yPos - 40)
                        DISPLAY.blit(text, textRect)
                        pygame.display.update()
                        time.sleep(3)
                        while not isConfig:
                            isConfig = (index+1) >= len(inputManager.buttons)
                            button = inputManager.buttons[index]
                            text = gameFont.render("Press the %s button..."%button, True, (255,255,255))
                            textRect = text.get_rect()
                            textRect.center = (200, yPos)
                            DISPLAY.blit(text, textRect)
                            pygame.display.update()
                            inputManager.getEvents()
                            success = inputManager.configButton(button)
                            if success:
                                index +=1
                                yPos += 40

                        inputManager.save_config()
                        waiting = False
                        
            # handle inputs and move in menu accordingly    
            if inputManager.isPressed("up"):
                waiting = False
                menuPos -= 1
            if inputManager.isPressed("down"):
                waiting = False
                menuPos += 1
        fpsClock.tick(FPS) # wait...

# create new enemies when one is killed
def newEnemy(which=0):
    """passing zero in will generate a random enemy"""
    global enemies
    if which == 0:
        location = random.randint(1, 100)
    elif which == 1: location = 20
    elif which == 2: location = 40
    elif which == 3: location = 80
    if location > 0 and location < 31:
        #create a rat
        randY = -(camY)+ (random.randint(4300, 4800))
        randX = -(camX)+ (random.randint(1000, 5000))
        NewEnemy = Enemy(randX, randY, player.level, (player.level * 50), (player.level + 9), (player.level+1),1,1,1,5,5, (player.level*50), "UP", 2,1) # create an instance of the player object
        enemies.append(NewEnemy)
        i = (len(enemies)-1)
        enemies[i].load_images("up", ["images\Rat\RatUP.png"])
        enemies[i].load_images("down", ["images\Rat\RatDOWN.png"])
        enemies[i].load_images("horizontal", ["images\Rat\RatRIGHT.png"])
        enemies[i].animate(0)
    if location > 30 and location < 76:
        #create a demon
        randY = -(camY)+ (random.randint(2500,3500))
        randX = -(camX)+ (random.randint(1000,5000))
        NewEnemy = Enemy(randX, randY, (player.level), (player.level * 150), (player.level + 15), (player.level+15),3,1,1,7,25,(player.level*250), "UP", 3,1) # create an instance of the player object
        enemies.append(NewEnemy)
        i = (len(enemies)-1)
        enemies[i].load_images("up", ["images\Demon\demonUP.png"])
        enemies[i].load_images("down", ["images\Demon\demonDOWN.png"])
        enemies[i].load_images("horizontal", ["images\Demon\demonRIGHT.png"])
        enemies[i].animate(0)
    if location > 75:
        #create a skeleton
        randY = -(camY)+  (random.randint(1000, 2000))
        randX = -(camX)+ (random.randint(2000, 5000))
        NewEnemy = Enemy(randX, randY, (player.level + 1), (player.level * 300), (player.level + 30), (player.level+30),3,1,1,5,50,(player.level*1000), "UP", 3,1) # create an instance of the player object
        enemies.append(NewEnemy)
        i = (len(enemies)-1)
        enemies[i].load_images("up", ["images\Skull\skullUP.png"])
        enemies[i].load_images("down", ["images\Skull\skullDOWN.png"])
        enemies[i].load_images("horizontal", ["images\Skull\skullRIGHT.png"])
        enemies[i].animate(0)
    
# setup new game
def newGame():
    global enemies, bounds, deathtraps, items, stores
    enemies = []
    #create the various enemies in the game
    for i in range(25):
        newEnemy(1)
    for i in range(35):
        newEnemy(2)
    for i in range(20):
        newEnemy(3)
    global bounds, deathtraps, items
    #initialize game objects
    bounds = []
    deathtraps = []
    items = []
    stores = []
    #create 4 vertical bounds
    objects = GameObjects("images\VertBound.png", 160, -2900)
    bounds.append(objects)
    objects = GameObjects("images\VertBound.png", 6850, -2900)
    bounds.append(objects)
    objects = GameObjects("images\VertBound.png", 160, -240)
    bounds.append(objects)
    objects = GameObjects("images\VertBound.png", 6850, -240)
    bounds.append(objects)
    #create the long horizontal bounds
    objects = GameObjects("images\LongBound.png", 1090, 970)
    bounds.append(objects)
    objects = GameObjects("images\LongBound.png", 2700, 970)
    bounds.append(objects)
    objects = GameObjects("images\LongBound.png", 4300, 970)
    bounds.append(objects)
    objects = GameObjects("images\LongBound.png", 5900, 970)
    bounds.append(objects)
    objects = GameObjects("images\LongBound.png", 1100, -320)
    bounds.append(objects)
    objects = GameObjects("images\LongBound.png", 2700, -320)
    bounds.append(objects)
    objects = GameObjects("images\LongBound.png", 4300, -320)
    bounds.append(objects)
    objects = GameObjects("images\LongBound.png", 1100, -1600)
    bounds.append(objects)
    objects = GameObjects("images\LongBound.png", 1100, -3040)
    bounds.append(objects)
    objects = GameObjects("images\MountainBound.png", 1100, -4250)
    bounds.append(objects)
    objects = GameObjects("images\MountainBound.png", 2700, -4250)
    bounds.append(objects)
    objects = GameObjects("images\MountainBound.png", 4300, -4250)
    bounds.append(objects)
    objects = GameObjects("images\MountainBound.png", 5900, -4250)
    bounds.append(objects)
    objects = GameObjects("images\MountainBound.png", 4300, -2560)
    bounds.append(objects)
    objects = GameObjects("images\MountainBound.png", 5900, -2560)
    bounds.append(objects)
    #create some other bounds
    objects = GameObjects("images\ShortBound.png", 1600, -2560)
    bounds.append(objects)
    objects = GameObjects("images\ShortBound.png", 1600, -2880)
    bounds.append(objects)
    objects = GameObjects("images\ShortBound.png", 6500, -320)
    bounds.append(objects)
    objects = GameObjects("images\ShortBound.png", 4800, -1600)
    bounds.append(objects)
    objects = GameObjects("images\ShortBound.png", 5300, -1600)
    bounds.append(objects)
    #create the stores....
    store = GameObjects("images\Store.png", 1600, -100, 0, False, True, "store")
    stores.append(store)
    store = GameObjects("images\Store.png", 5100, -1350, 0, False, True, "store")
    stores.append(store)
    #create the games various deathtraps
    for i in range(120):
        if i < 20:
            randX = random.randint(2000, 5800)
            randY = random.randint(200, 700)
        if i > 19 and i < 70:
            randX = random.randint(2500, 4000)
            randY = -(random.randint(1000, 2000))
        if i > 69:
            randX = random.randint(2000, 5800)
            randY = -(random.randint(3000,3800)) 
        objects = GameObjects("images\DEATH.png", randX, randY, 1, True, False)
        deathtraps.append(objects)
    #create the games starting items
    for i in range(20):
        randX = random.randint(2000, 5000)
        if i < 5:
            randY = random.randint(300, 700)
        if i > 4 and i < 15:
            randY = -(random.randint(700, 1400))
        if i > 14:
            randY = -(random.randint(3000, 3800))
        objects = GameObjects("images\potion.png", randX, randY, 0, False, True, "potion")
        items.append(objects)

# displays the magic selection menu
def showMagicMenu():
    inMenu = True
    menuPos = (player.spells.index(player.curSpell) * 10)
    while inMenu:
        pygame.draw.rect(DISPLAY, (0,0,0), (0,60,200, len((player.spells*50))))
        pygame.draw.rect(DISPLAY, (255,255,255), (0,60,200, len((player.spells*50))), 4)
        if menuPos > ((len(player.spells) * 10) - 1):
            menuPos = ((len(player.spells) * 10) - 1)
        if menuPos < 0: menuPos = 0
        #setup the menu text according to menuPos
        if menuPos > -1 and menuPos < 10:
            if len(player.spells) > 0:
                text = gameFont.render("> %s"%player.spells[0], True, WHITE)
        else:
            if len(player.spells) > 0:
                text = gameFont.render("  %s"%player.spells[0], True, WHITE)
        if len(player.spells) > 0: DISPLAY.blit(text, (30,90))
        if menuPos > 9 and menuPos < 20:
            if len(player.spells) > 1:
                text = gameFont.render("> %s"%player.spells[1], True, WHITE)
        else:
            if len(player.spells) > 1:
                text = gameFont.render("  %s"%player.spells[1], True, WHITE)
        if len(player.spells) > 1: DISPLAY.blit(text, (30,130))
        if menuPos > 19 and menuPos < 30:
            if len(player.spells) > 2:
                text = gameFont.render("> %s"%player.spells[2], True, WHITE)
        else:
            if len(player.spells) > 2:
                text = gameFont.render("  %s"%player.spells[2], True, WHITE)
        if len(player.spells) > 2: DISPLAY.blit(text, (30,170))
        if menuPos > 29:
            if len(player.spells) > 3:
                text = gameFont.render("> %s"%player.spells[3], True, WHITE)
        else:
            if len(player.spells) > 3:
                text = gameFont.render("  %s"%player.spells[3], True, WHITE)
        if len(player.spells) > 3: DISPLAY.blit(text, (30,210))
                
        pygame.display.update()
        waiting = True
        while waiting:
            #handle keyboard/joystick input
            for event in inputManager.getEvents():
                if event.key == "B" and event.down:
                    if menuPos > -1 and menuPos < 10:
                        player.curSpell = player.spells[0]
                        player.spellImg = player.spellImages[0]
                        player.spellRect = player.spellImg.get_rect()
                        player.mpCost = 10
                    if menuPos > 9 and menuPos < 20:
                        player.curSpell = player.spells[1]
                        player.spellImg = player.spellImages[1]
                        player.spellRect = player.spellImg.get_rect()
                        player.mpCost = 25
                    if menuPos > 19 and menuPos < 30:
                        player.curSpell = player.spells[2]
                        player.spellImg = player.spellImages[2]
                        player.spellRect = player.spellImg.get_rect()
                        player.mpCost = 50
                    if menuPos > 29:
                        player.curSpell = player.spells[3]
                        player.spellImg = player.spellImages[3]
                        player.spellRect = player.spellImg.get_rect()
                        player.mpCost = 100
                    waiting = False
                    inMenu = False
                                                       
                if event.key == "L" and event.down:
                    waiting = False
                    inMenu = False
                    
            # handle inputs and move in menu accordingly    
            if inputManager.isPressed("up"):
                waiting = False
                menuPos -= 1
            if inputManager.isPressed("down"):
                waiting = False
                menuPos += 1
        fpsClock.tick(FPS) # wait...

# creates the game menu and pauses the game while displaying various game info
def showGameMenu():
    inMenu = True
    menuPos = 2
    while inMenu:
        pygame.draw.rect(DISPLAY, (0,0,0), (400, 250, 500, 400))
        pygame.draw.rect(DISPLAY, (255,255,255), (400,250, 150, 400), 4)
        pygame.draw.rect(DISPLAY, (255,255,255), (550,250, 350, 400), 4)
        if player.levelUp:
            if menuPos > 49:
                menuPos = 50
        else:
            if menuPos > 49:
                menuPos = 49
        if menuPos < 0: menuPos = 0
        #setup the menu text according to menuPos
        if menuPos > -1 and menuPos < 10:
            showStats()
            text = gameFont.render("> STATS", True, WHITE)
        else:
            text = gameFont.render("  STATS", True, WHITE)
        DISPLAY.blit(text, (420,270))
        if menuPos > 9 and menuPos < 20:
            showItems()
            text = gameFont.render("> ITEMS", True, WHITE)
        else:
            text = gameFont.render("  ITEMS", True, WHITE)
        DISPLAY.blit(text, (420,300))
        if menuPos > 19 and menuPos < 30:
            showMagic()
            text = gameFont.render("> MAGIC", True, WHITE)
        else:
            text = gameFont.render("  MAGIC", True, WHITE)
        DISPLAY.blit(text, (420,330))
        if menuPos > 29 and menuPos < 40:
            text = gameFont.render("> QUIT", True, WHITE)
        else:
            text = gameFont.render("  QUIT", True, WHITE)
        DISPLAY.blit(text, (420,360))
        if menuPos > 39 and menuPos < 50:
            text = gameFont.render("> SAVE", True, WHITE)
        else:
            text = gameFont.render("  SAVE", True, WHITE)
        DISPLAY.blit(text, (420,390))
        if menuPos > 49:
            text = gameFont.render("> LEVEL UP", True, WHITE)
        else:
            text = gameFont.render("  LEVEL UP", True, WHITE)
        if player.levelUp: DISPLAY.blit(text, (420, 420))
        pygame.display.update()
        waiting = True
        while waiting:
            #handle keyboard/joystick input
            for event in inputManager.getEvents():
                if event.key == "B" and event.down:
                    if menuPos > 29 and menuPos < 40:
                        waiting = False
                        inMenu = False
                        mainMenu()
                    if menuPos > 39 and menuPos < 50:
                        saveGame()
                    if menuPos > 49:
                        levelUP()
                    waiting = False
                                                       
                if event.key == "start" and event.down:
                    waiting = False
                    inMenu = False
                    
            # handle inputs and move in menu accordingly    
            if inputManager.isPressed("up"):
                waiting = False
                menuPos -= 1
            if inputManager.isPressed("down"):
                waiting = False
                menuPos += 1
        fpsClock.tick(FPS) # wait...

# save the current gamestate (player stats only...)
def saveGame():
    gameState = [player.level, player.totHP, player.strength, player.wisdom,
                 player.defense, player.luck, player.criticalPerc, player.speed,
                 player.gold, player.exp, player.direction]
    myFile = open("data\saveGame.dat", "w")
    cPickle.dump(gameState, myFile)
    myFile.close()
    myFile = open("data\playerItems.dat", "w")
    cPickle.dump(player.items, myFile)
    myFile.close()
    myFile = open("data\playerSpells.dat", "w")
    cPickle.dump(player.spells, myFile)
    myFile.close()
    myFile = open("data\storeInv.dat", "w")
    cPickle.dump(storeInv, myFile)
    myFile.close()

# loads the current save game
def loadGame():
    global player, camX, camY, storeInv
    myFile = open("data\saveGame.dat", "r")
    gameState = cPickle.load(myFile)
    myFile.close()
    player.__init__(640, 400, gameState[0], gameState[1], gameState[2], gameState[3],gameState[4],gameState[5],gameState[6],gameState[7],gameState[8],gameState[9],gameState[10])
    player.load_images("up", ["images\Player\playerUP.png"])
    player.load_images("attack-up", ["images\Player\playerATTACKUP.png"])
    player.load_images("down", ["images\Player\playerDOWN.png"])
    player.load_images("attack-down", ["images\Player\playerATTACKDOWN.png"])
    player.load_images("horizontal", ["images\Player\playerHOR.png"])
    player.load_images("attack-horizontal", ["images\Player\playerHORATTACK.png"])
    player.load_images("dead", ["images\Player\playerDEAD.png"])
    myFile = open("data\playerItems.dat", "r")
    player.items = cPickle.load(myFile)
    myFile.close()
    myFile = open("data\playerSpells.dat", "r")
    player.spells = cPickle.load(myFile)
    myFile.close()
    myFile = open("data\storeInv.dat", "r")
    storeInv = cPickle.load(myFile)
    myFile.close()
    spell = pygame.image.load("images\Heal.png")
    player.spellImages.append(spell)
    spell = pygame.image.load("images\Fireball.png")
    player.spellImages.append(spell)
    spell = pygame.image.load("images\Frost.png")
    player.spellImages.append(spell)
    spell = pygame.image.load("images\Oblivion.png")
    player.spellImages.append(spell)
    player.animate(0)
    background.__init__(320,4480)
    background.load_tiles(["tiles\grass.png", "tiles\stone.png", "tiles\water.png"])
    camX = 320
    camY = 4480
    newGame()
    mainGame()
                 
# shows the players stats on the game menu
def showStats():
    text = gameFont.render("LEVEL: %d"%player.level,True,WHITE)
    DISPLAY.blit(text, (570,260))
    text = gameFont.render("HEALTH: %d/%d"%(player.curHP,player.totHP),True,WHITE)
    DISPLAY.blit(text, (570,300))
    text = gameFont.render("STRENGTH: %d"%player.strength,True,WHITE)
    DISPLAY.blit(text, (570,340))
    text = gameFont.render("WISDOM: %d"%player.wisdom,True,WHITE)
    DISPLAY.blit(text, (570,380))
    text = gameFont.render("LUCK: %d"%player.luck,True,WHITE)
    DISPLAY.blit(text, (570,420))
    text = gameFont.render("SPEED: %d    DEFENSE: %d"%(player.speed/5, player.defense),True,WHITE)
    DISPLAY.blit(text, (570,460))
    text = gameFont.render("CRITICAL: %d + %d"%(player.criticalPerc, player.luck),True,WHITE)
    DISPLAY.blit(text, (570,500))
    text = gameFont.render("GOLD: %d"%player.gold,True,WHITE)
    DISPLAY.blit(text, (570,540))
    text = gameFont.render("XP: %d"%player.exp,True,WHITE)
    DISPLAY.blit(text, (570,580))
    text = gameFont.render("NEXT LVL: %d"%player.nextLevel,True,WHITE)
    DISPLAY.blit(text, (570,620))

# shows the players current items on the game menu
def showItems():
    yPos = 300
    text = gameFont.render("ITEMS:", True, WHITE)
    DISPLAY.blit(text, (570, 260))
    for item in player.items:
        text = gameFont.render("%s: %d"%(item.upper(), player.items[item]), True, WHITE)
        DISPLAY.blit(text, (570, yPos))
        yPos += 30

# shows the players available magic spells
def showMagic():
    yPos = 300
    text = gameFont.render("MAGIC:", True, WHITE)
    DISPLAY.blit(text, (570, 260))
    for spell in player.spells:
        if spell == "Heal": mpCost = 10
        if spell == "Fireball": mpCost = 25
        if spell == "Frost": mpCost = 50
        if spell == "Oblivion": mpCost = 100
        text = gameFont.render("%s: %d MP"%(spell.upper(), mpCost), True, WHITE)
        DISPLAY.blit(text, (570, yPos))
        yPos += 30
    text = gameFont.render("MP: %d/%d"%(player.curMP, player.totMP), True, WHITE)
    DISPLAY.blit(text, (570, 620))

#show the store inventory and let the player purchase
def storeMenu():
    inStore = True
    menuPos = 2
        
    while inStore:
        cost = 0
        yPos = 350
        storeQty = len(storeInv)
        storeItem = []
        for item in storeInv:
            storeItem.append(item)
        pygame.draw.rect(DISPLAY, (0,0,0), (450, 300, 350, 350))
        pygame.draw.rect(DISPLAY, (255,255,255), (450, 300, 350, 350), 4)
        if menuPos > ((storeQty * 10) - 1):
            menuPos = ((storeQty * 10) - 1)
        if menuPos < 0: menuPos = 0
        text = gameFont.render("STORE:", True, WHITE)
        DISPLAY.blit(text, (470, 310))
        if menuPos > -1 and menuPos < 10:
            if storeQty > 0:
                text = gameFont.render("> %s: %d in stock"%(storeItem[0].upper(), storeInv[storeItem[0]]), True, WHITE)
        else:
            if storeQty > 0:
                text = gameFont.render("  %s: %d in stock"%(storeItem[0].upper(), storeInv[storeItem[0]]), True, WHITE)
        if storeQty > 0:
            DISPLAY.blit(text, (470,yPos))
            yPos += 30
        if menuPos > 9 and menuPos < 20:
            if storeQty > 1:
                text = gameFont.render("> %s: %d in stock"%(storeItem[1].upper(), storeInv[storeItem[1]]), True, WHITE)
        else:
            if storeQty > 1:
                text = gameFont.render("  %s: %d in stock"%(storeItem[1].upper(), storeInv[storeItem[1]]), True, WHITE)
        if storeQty > 1:
            DISPLAY.blit(text, (470,yPos))
            yPos += 30
        if menuPos > 19 and menuPos < 30:
            if storeQty > 2:
                text = gameFont.render("> %s: %d in stock"%(storeItem[2].upper(), storeInv[storeItem[2]]), True, WHITE)
        else:
            if storeQty > 2:
                text = gameFont.render("  %s: %d in stock"%(storeItem[2].upper(), storeInv[storeItem[2]]), True, WHITE)
        if storeQty > 2:
            DISPLAY.blit(text, (470,yPos))
            yPos += 30
        if storeItem[(menuPos/10)] == "potion":
            cost = 250
        elif storeItem[(menuPos/10)] == "Frost":
            cost = 1000
        elif storeItem[(menuPos/10)] == "Oblivion":
            cost = 10000
        text = gameFont.render("ITEM COST: %d"%(cost), True, WHITE)
        DISPLAY.blit(text, (470, 470))
        text = gameFont.render("PLAYER GOLD: %d"%(player.gold), True, WHITE)
        DISPLAY.blit(text, (470, 500))
        pygame.display.update()
        waiting = True
        while waiting:
            #handle keyboard/joystick input
            for event in inputManager.getEvents():
                if event.key == "B" and event.down:    
                    if storeQty > 0:
                        if storeItem[(menuPos/10)] == "Frost":
                            cost = 1000
                        elif storeItem[(menuPos/10)] == "Oblivion":
                            cost = 10000
                        elif storeItem[(menuPos/10)] == "potion":
                            cost = 250
                    else:
                        cost = 0
                        
                    if cost == 250 and player.gold >= 250:
                        player.gold -= 250
                        storeInv[storeItem[(menuPos/10)]] -= 1
                        if "potion" in player.items:
                            player.items["potion"] += 1
                        else:
                            player.items["potion"] = 1
                        if storeInv[storeItem[(menuPos/10)]] <= 0:
                            del storeInv[storeItem[(menuPos/10)]]
                    elif cost == 1000 and player.gold >= 1000:
                        player.gold -= cost
                        player.spells.append(storeItem[(menuPos/10)])
                        del storeInv[storeItem[(menuPos/10)]]
                    elif cost == 10000 and player.gold >= 10000:
                        player.gold -= cost
                        player.spells.append(storeItem[(menuPos/10)])
                        del storeInv[storeItem[(menuPos/10)]]
                    
                    waiting = False
                                        
                if event.key == "A" and event.down:
                    waiting = False
                    inStore = False
                    
            # handle inputs and move in menu accordingly    
            if inputManager.isPressed("up"):
                waiting = False
                menuPos -= 1
            if inputManager.isPressed("down"):
                waiting = False
                menuPos += 1
        fpsClock.tick(FPS) # wait...
                                        
# levelup the players character
def levelUP():
    inLEVEL = True
    menuPos = 2
    points = 10
    while inLEVEL:
        pygame.draw.rect(DISPLAY, (0,0,0), (450, 300, 300, 300))
        pygame.draw.rect(DISPLAY, (255,255,255), (450, 300, 300, 300), 4)
        if menuPos > 50:
            menuPos = 50
        if menuPos < 0: menuPos = 0
        text = gameFont.render("POINTS LEFT: %d"%points, True, WHITE)
        DISPLAY.blit(text, (470, 310))
        #setup the menu text according to menuPos
        if menuPos > -1 and menuPos < 10:
            text = gameFont.render("> STRENGTH: %d"%player.strength, True, WHITE)
        else:
            text = gameFont.render("  STRENGTH: %d"%player.strength, True, WHITE)
        DISPLAY.blit(text, (470,350))
        if menuPos > 9 and menuPos < 20:
            text = gameFont.render("> WISDOM: %d"%player.wisdom, True, WHITE)
        else:
            text = gameFont.render("  WISDOM: %d"%player.wisdom, True, WHITE)
        DISPLAY.blit(text, (470,380))
        if menuPos > 19 and menuPos < 30:
            text = gameFont.render("> LUCK: %d"%player.luck, True, WHITE)
        else:
            text = gameFont.render("  LUCK: %d"%player.luck, True, WHITE)
        DISPLAY.blit(text, (470,410))
        if menuPos > 29 and menuPos < 40:
            text = gameFont.render("> SPEED: %d"%(player.speed/5), True, WHITE)
        else:
            text = gameFont.render("  SPEED: %d"%(player.speed/5), True, WHITE)
        DISPLAY.blit(text, (470,440))
        if menuPos > 39 and menuPos < 50:
            text = gameFont.render("> TOTAL HP: %d"%player.totHP, True, WHITE)
        else:
            text = gameFont.render("  TOTAL HP: %d"%player.totHP, True, WHITE)
        DISPLAY.blit(text, (470,470))
        if menuPos > 49:
            text = gameFont.render("> FINISHED", True, WHITE)
        else:
            text = gameFont.render("  FINISHED", True, WHITE)
        DISPLAY.blit(text, (470,520))
        pygame.display.update()
        waiting = True
        while waiting:
            #handle keyboard/joystick input
            for event in inputManager.getEvents():
                if event.key == "B" and event.down:
                    if points > 0:
                        if menuPos > -1 and menuPos < 10:
                            player.strength += 1
                            points -= 1
                        if menuPos > 9 and menuPos < 20:
                            player.wisdom += 1
                            points -= 1
                        if menuPos > 19 and menuPos < 30:
                            player.luck += 1
                            points -= 1
                        if menuPos > 29 and menuPos < 40:
                            player.speed += 5
                            points -= 1
                        if menuPos > 39 and menuPos < 50:
                            player.totHP += 50
                            points -= 1
                    if menuPos > 49:
                        player.levelUp = False
                        player.updateStats()
                        inLEVEL = False
                    waiting = False
                if event.key == "A" and event.down:
                    if menuPos > -1 and menuPos < 10:
                        if player.strength > 0:
                            player.strength -= 1
                            points += 1
                    if menuPos > 9 and menuPos < 20:
                        if player.wisdom > 0:
                            player.wisdom -= 1
                            points += 1
                    if menuPos > 19 and menuPos < 30:
                        if player.luck > 0:
                            player.luck -= 1
                            points += 1
                    if menuPos > 29 and menuPos < 40:
                        if player.speed > 0:
                            player.speed -= 5
                            points += 1
                    if menuPos > 39 and menuPos < 50:
                        if player.totHP > 0:
                            player.totHP -= 50
                            points += 1
                    waiting = False
                    
            # handle inputs and move in menu accordingly    
            if inputManager.isPressed("up"):
                waiting = False
                menuPos -= 1
            if inputManager.isPressed("down"):
                waiting = False
                menuPos += 1
        fpsClock.tick(FPS) # wait...
                               
# creates the player's HUD displaying certain info
def drawHUD():
    pygame.draw.rect(DISPLAY, BLACK, (0,0,1280,60))
    pygame.draw.rect(DISPLAY, WHITE, (0,0,1280,60), 4)
    text = gameFont.render("Lvl: %d"%player.level,True,WHITE)
    DISPLAY.blit(text, (15,20))
    text = gameFont.render("HP: %d/%d"%(player.curHP,player.totHP),True,WHITE)
    DISPLAY.blit(text, (90,20))
    text = gameFont.render("STR: %d"%player.strength,True,WHITE)
    DISPLAY.blit(text, (300,20))
    text = gameFont.render("WIS: %d"%player.wisdom,True,WHITE)
    DISPLAY.blit(text, (400,20))
    if "potion" in player.items:
        numPotions = player.items["potion"]
    else:
        numPotions = 0
    text = gameFont.render(": %d"%numPotions,True,WHITE)
    DISPLAY.blit(potionIcon, (500,10))
    DISPLAY.blit(text, (535,20))
    text = gameFont.render(": %d"%player.gold,True,WHITE)
    DISPLAY.blit(coinIcon, (587,17))
    DISPLAY.blit(text, (620,20))
    text = gameFont.render("XP: %d"%player.exp,True,WHITE)
    DISPLAY.blit(text, (720,20))
    text = gameFont.render("NEXT LVL: %d"%player.nextLevel,True,WHITE)
    DISPLAY.blit(text, (865,20))
    text = gameFont.render("MP: %d/%d"%(player.curMP,player.totMP),True,WHITE)
    DISPLAY.blit(text, (1120,20))
    
# if the player dies, show the game over screen
def gameOver():
    pygame.mixer.music.load("music\Gameover.mp3") # load the file to the music mixer
    pygame.mixer.music.play(-1,0.0) # play the file loaded in the mixer
    while True:
        for event in inputManager.getEvents():
            if event.key == "start" and event.down:
                mainMenu()
        imageRect = go1Image.get_rect()
        imageRect.center = (640, 200)
        DISPLAY.blit(go1Image, imageRect)
        imageRect = go2Image.get_rect()
        imageRect.center = (640, 500)
        DISPLAY.blit(go2Image, imageRect)
        pygame.display.update()
        
#move the game up
def moveUp():
    global camY
    player.direction = "UP"
    background.change_cam(0, player.speed)
    #change each game object
    for bound in bounds:
        bound.move(0,player.speed)
    for deathtrap in deathtraps:
        deathtrap.move(0,player.speed)
    for item in items:
        item.move(0,player.speed)
    for store in stores:
        store.move(0,player.speed)
    for enemy in enemies:
        enemy.move(0,-player.speed)
    if player.isCasting and not player.curSpell == "Heal":
        player.spellY += player.speed
    #change the relative camera variable
    camY -= player.speed
    
#move the game down
def moveDown():
    global camY
    player.direction = "DOWN"
    background.change_cam(0, -player.speed)
    #change each game object
    for bound in bounds:
        bound.move(0,-player.speed)
    for deathtrap in deathtraps:
        deathtrap.move(0,-player.speed)
    for item in items:
        item.move(0,-player.speed)
    for store in stores:
        store.move(0,-player.speed)
    for enemy in enemies:
        enemy.move(0,player.speed)
    if player.isCasting and not player.curSpell == "Heal":
        player.spellY -= player.speed
    #change the relative camera variable
    camY += player.speed
    
#move the game left    
def moveLeft():
    global camX
    player.direction = "LEFT"
    background.change_cam(player.speed, 0)
    #change each game object
    for bound in bounds:
        bound.move(player.speed,0)
    for deathtrap in deathtraps:
        deathtrap.move(player.speed,0)
    for item in items:
        item.move(player.speed,0)
    for store in stores:
        store.move(player.speed,0)
    for enemy in enemies:
        enemy.move(player.speed,0)
    if player.isCasting and not player.curSpell == "Heal":
        player.spellX += player.speed
    #change the relative camera variable
    camX -= player.speed
            
#move the game right
def moveRight():
    global camX
    player.direction = "RIGHT"
    background.change_cam(-player.speed, 0)
    #move each game object
    for bound in bounds:
        bound.move(-player.speed,0)
    for deathtrap in deathtraps:
        deathtrap.move(-player.speed,0)
    for item in items:
        item.move(-player.speed,0)
    for store in stores:
        store.move(-player.speed,0)
    for enemy in enemies:
        enemy.move(-player.speed,0)
    if player.isCasting and not player.curSpell == "Heal":
        player.spellX -= player.speed
    #change the relative camera variable
    camX += player.speed

# test for collisions amongst all object and handle accordingly
def detectCollisions():
    #test player and enemys against the bounds and adjust accordingly
    for bound in bounds:
        if player.charRect.colliderect(bound.objRect):
            #we have a collision, now where are the rectangles in relation to one another
            if player.charRect.centerx > bound.objRect.centerx:
                moveRight()
            else:
                moveLeft()
            if player.charRect.centery > bound.objRect.centery:
                moveDown()
            else:
                moveUp()
        #check for enemies against the bounds
        for enemy in enemies:
            if enemy.charRect.colliderect(bound.objRect):
                if enemy.charRect.centerx > bound.objRect.centerx:
                    enemy.move(enemy.speed, 0)
                else:
                    enemy.move(-enemy.speed, 0)
                if enemy.charRect.centery > bound.objRect.centery:
                    enemy.move(0,-enemy.speed)
                else:
                    enemy.move(0,enemy.speed)
                    
    #check to see if the player wants to shop...
    for store in stores:
        if player.charRect.colliderect(store.objRect) and player.interact:
            storeMenu()
            player.interact = False
            
    #detect player collisions with death traps and items
    for deathtrap in deathtraps:
        if player.charRect.colliderect(deathtrap.objRect):
            player.curHP -= deathtrap.damageFactor
    for item in items:
        if player.charRect.colliderect(item.objRect):
            if item.typeOf == "coin":
                coinSound.play()
                player.gold += 10
            elif item.typeOf == "potion":
                potionSound.play()
                if "potion" in player.items:
                    player.items["potion"] += 1
                else:
                    player.items["potion"] = 1
            items.remove(item)
            
    #detect player collisions against every enemy and damage player hp if touching
    for enemy in enemies:
        for otherEnemy in enemies:
            if enemy.charRect.colliderect(otherEnemy.charRect) and not enemy == otherEnemy:
                if enemy.charRect.centerx > otherEnemy.charRect.centerx:
                    enemy.direction = "UP"
                else:
                    enemy.direction = "DOWN"
                if enemy.charRect.centery > otherEnemy.charRect.centery:
                    enemy.direction = "LEFT"
                else:
                    enemy.direction = "RIGHT"
        if player.isCasting and player.spellRect.colliderect(enemy.charRect):
            if player.curSpell == "Oblivion":
                enemy.curHP -= (player.wisdom * (player.level + 5)) - ((enemy.wisdom + enemy.level)/2)
            elif player.curSpell == "Frost":
                enemy.curHP -= (player.wisdom * (player.level + 2)) - ((enemy.wisdom + enemy.level)/2)
                player.isCasting = False
            elif player.curSpell == "Fireball":
                enemy.curHP -= (player.wisdom * player.level) - ((enemy.wisdom + enemy.level)/2)
                player.isCasting = False
            
        if player.charRect.colliderect(enemy.charRect):
            if enemy.direction == "UP":
                enemy.move(0,(-enemy.speed*2))
            elif enemy.direction == "DOWN":
                enemy.move(0,(enemy.speed*2))
            elif enemy.direction == "RIGHT":
                enemy.move((-enemy.speed*2),0)
            elif enemy.direction == "LEFT":
                enemy.move((enemy.speed*2),0)
            # this will keep the enemy from killing the player really quickly
            if animPOS == 5:
                critical = (random.randint(1,100) <= (enemy.criticalPerc+enemy.luck))
                if critical:
                    damage = ((((enemy.strength+enemy.luck)*2)*(enemy.level))*2)-(player.defense)
                else:
                    damage = ((enemy.strength*2)*enemy.level)-(player.defense)
                if damage > 0:
                    player.curHP -= damage
            #if the player isAttacking, then do damage to enemy
            if player.isAttacking and animPOS == 5:
                critical = (random.randint(1,100) <= (player.criticalPerc+player.luck))
                if critical:
                    damage = ((((player.strength+player.luck)*2)*(player.level))*2)-(enemy.defense)
                else:
                    damage = ((player.strength*2)*player.level)-(enemy.defense)
                if damage > 0:
                    enemy.curHP -= damage
                swordSound.play()
                player.isAttacking = False
        
#this function will create all coins dropped by a dead enemy
def dropCoins(x, y, coins, gained):
    player.exp += gained
    if player.exp >= player.nextLevel:
        player.levelUp = True
    for i in range(coins):
        randX = random.randint(x-100, x+100)
        randY = random.randint(y-25, y+25)
        coin = GameObjects("images\coin.png", randX, randY, 0, False, True, "coin")
        items.append(coin)

# this funtion will handle if the player can use a potion or not
def usePotion():
    if "potion" in player.items:
        numPotions = player.items["potion"]
    else:
        numPotions = 0
    if numPotions > 0:
        player.items["potion"] -= 1
        potionSound.play()
        player.curHP += (player.wisdom + player.level) * 5
    
#when we want to terminate the game, we call this function
def terminate():
    pygame.quit()
    sys.exit()

#well, we need to run the game!
mainMenu()
