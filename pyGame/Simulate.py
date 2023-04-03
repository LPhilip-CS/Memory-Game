# Simulate (a Simon says game)

import random, sys, time, pygame
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FLASHSPEED = 500  # in milliseconds
FLASHDELAY = 1000  # in milliseconds
BUTTONSIZE = 200
BUTTONGAPSIZE = 20
TIMEOUT = 4  # seconds before game over if no button is pushed.

#                R    G    B
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BRIGHTRED = (255, 0, 0)
RED = (155, 0, 0)
BRIGHTGREEN = (0, 255, 0)
GREEN = (0, 155, 0)
BRIGHTBLUE = (0, 0, 255)
BLUE = (0, 0, 155)
BRIGHTYELLOW = (255, 255, 0)
YELLOW = (155, 155, 0)
DARKGRAY = (40, 40, 40)
bgColor = BLACK

XMARGIN = int((WINDOWWIDTH - (2 * BUTTONSIZE) - BUTTONGAPSIZE) / 2)
YMARGIN = int((WINDOWHEIGHT - (2 * BUTTONSIZE) - BUTTONGAPSIZE) / 2)

# Rect objects for each of the four buttons
YELLOWRECT = pygame.Rect(XMARGIN, YMARGIN, BUTTONSIZE, BUTTONSIZE)
BLUERECT = pygame.Rect(XMARGIN + BUTTONSIZE + BUTTONGAPSIZE, YMARGIN, BUTTONSIZE, BUTTONSIZE)
REDRECT = pygame.Rect(XMARGIN, YMARGIN + BUTTONSIZE + BUTTONGAPSIZE, BUTTONSIZE, BUTTONSIZE)
GREENRECT = pygame.Rect(XMARGIN + BUTTONSIZE + BUTTONGAPSIZE, YMARGIN + BUTTONSIZE + BUTTONGAPSIZE, BUTTONSIZE,
                        BUTTONSIZE)


def song():
    channel1 = pygame.mixer.Channel(0)
    channel1.set_volume(.05)
    channel1.play(pygame.mixer.Sound('Sound1.ogg'), loops=-1)

def secondchannel():
    channel2 = pygame.mixer.Channel(1)
    channel2.set_volume(10000)
    channel2.play(pygame.mixer.Sound('GameStart.ogg'))
def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BEEP1, BEEP2, BEEP3, BEEP4
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=2 ** 12)
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Simulate')
    secondchannel()
    time.sleep(4)
    BASICFONT = pygame.font.Font('freesansbold.ttf', 16)
    infoSurf = BASICFONT.render('Match the pattern by clicking on the button or using the Q, W, A, S keys.', 1,
                                DARKGRAY)
    infoRect = infoSurf.get_rect()
    infoRect.topleft = (10, WINDOWHEIGHT - 25)

    # load the sound files
    BEEP1 = pygame.mixer.Sound('beep1.ogg')
    BEEP2 = pygame.mixer.Sound('beep2.ogg')
    BEEP3 = pygame.mixer.Sound('beep3.ogg')
    BEEP4 = pygame.mixer.Sound('beep4.ogg')
    song()

    # Initialize some variables for a new game
    pattern = []  # stores the pattern of colors
    currentStep = 0  # the color the player must push next
    lastClickTime = 0  # timestamp of the player's last button push
    score = 0
    # when False, the pattern is playing. when True, waiting for the player to click a colored button:
    waitingForInput = False

    while True:  # main game loop
        clickedButton = None  # button that was clicked (set to YELLOW, RED, GREEN, or BLUE)
        DISPLAYSURF.fill(bgColor)
        drawButtons()
        scoreSurf = BASICFONT.render('Score: ' + str(score), 1, WHITE)
        scoreRect = scoreSurf.get_rect()
        scoreRect.topleft = (WINDOWWIDTH - 100, 10)
        DISPLAYSURF.blit(scoreSurf, scoreRect)

        DISPLAYSURF.blit(infoSurf, infoRect)

        checkForQuit()
        for event in pygame.event.get():  # event handling loop
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                clickedButton = getButtonClicked(mousex, mousey)
            elif event.type == KEYDOWN:
                if event.key == K_q:
                    clickedButton = YELLOW
                elif event.key == K_w:
                    clickedButton = BLUE
                elif event.key == K_a:
                    clickedButton = RED
                elif event.key == K_s:
                    clickedButton = GREEN

        if not waitingForInput:
            # play the pattern
            pygame.display.update()
            pygame.time.wait(1000)
            if score == 0:
                pattern.append(GREEN)
                for button in pattern:
                    flashButtonAnimation(button)
                    pygame.time.wait(FLASHDELAY)
                waitingForInput = True
            if score != 0:
                pattern.append(random.choice((YELLOW, BLUE, RED, GREEN)))
                for button in pattern:
                    flashButtonAnimation(button)
                    pygame.time.wait(FLASHDELAY)
                waitingForInput = True
        else:
            # wait for the player to enter buttons
            if clickedButton and clickedButton == pattern[currentStep]:
                # pushed the correct button
                flashButtonAnimation(clickedButton)
                currentStep += 1
                lastClickTime = time.time()

                if currentStep == len(pattern):
                    # pushed the last button in the pattern
                    changeBackgroundAnimation()
                    score += 1
                    waitingForInput = False
                    currentStep = 0  # reset back to first step

            elif (clickedButton and clickedButton != pattern[currentStep]) or (
                    currentStep != 0 and time.time() - TIMEOUT > lastClickTime):
                # pushed the incorrect button, or has timed out
                gameOverAnimation()
                # reset the variables for a new game:
                pattern = []
                currentStep = 0
                waitingForInput = False
                score = 0
                pygame.time.wait(1000)
                changeBackgroundAnimation()

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


def checkForQuit():
    for event in pygame.event.get(QUIT):  # get all the QUIT events
        terminate()  # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP):  # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate()  # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event)  # put the other KEYUP event objects back


def flashButtonAnimation(color, animationSpeed=50):
    if color == YELLOW:
        sound = BEEP1
        flashColor = BRIGHTYELLOW
        rectangle = YELLOWRECT
    elif color == BLUE:
        sound = BEEP2
        flashColor = BRIGHTBLUE
        rectangle = BLUERECT
    elif color == RED:
        sound = BEEP3
        flashColor = BRIGHTRED
        rectangle = REDRECT
    elif color == GREEN:
        sound = BEEP4
        flashColor = BRIGHTGREEN
        rectangle = GREENRECT

    origSurf = DISPLAYSURF.copy()
    flashSurf = pygame.Surface((BUTTONSIZE, BUTTONSIZE))
    flashSurf = flashSurf.convert_alpha()
    r, g, b = flashColor

    sound.play().set_volume(10000)

    for start, end, step in ((0, 255, 1), (255, 0, -1)):  # animation loop
        for alpha in range(start, end, animationSpeed * step):
            checkForQuit()
            DISPLAYSURF.blit(origSurf, (0, 0))
            flashSurf.fill((r, g, b, alpha))
            DISPLAYSURF.blit(flashSurf, rectangle.topleft)
            pygame.display.update()
            FPSCLOCK.tick(FPS)
    DISPLAYSURF.blit(origSurf, (0, 0))


def drawButtons():
    
    # all squares
    pygame.draw.rect(DISPLAYSURF, BLUE, YELLOWRECT)
    pygame.draw.rect(DISPLAYSURF, WHITE,   BLUERECT)
    pygame.draw.rect(DISPLAYSURF, WHITE,    REDRECT)
    pygame.draw.rect(DISPLAYSURF, WHITE,  GREENRECT)
    # top right square
    pygame.draw.rect(DISPLAYSURF, RED, (330, 30, 200, 30))
    pygame.draw.rect(DISPLAYSURF, RED, (330, 85, 200, 30))
    pygame.draw.rect(DISPLAYSURF, RED, (330, 145, 200, 30))
    pygame.draw.rect(DISPLAYSURF, RED, (330, 200, 200, 30))
    # bottom right square
    pygame.draw.rect(DISPLAYSURF, RED, (330, 250, 200, 30))
    pygame.draw.rect(DISPLAYSURF, RED, (330, 310, 200, 30))
    pygame.draw.rect(DISPLAYSURF, RED, (330, 365, 200, 30))
    pygame.draw.rect(DISPLAYSURF, RED, (330, 420, 200, 30))
    # bottom left square
    pygame.draw.rect(DISPLAYSURF, RED, (110, 250, 200, 30))
    pygame.draw.rect(DISPLAYSURF, RED, (110, 310, 200, 30))
    pygame.draw.rect(DISPLAYSURF, RED, (110, 365, 200, 30))
    pygame.draw.rect(DISPLAYSURF, RED, (110, 420, 200, 30))

    # 50 stars
    pygame.draw.circle(DISPLAYSURF, WHITE, (120, 40), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (160, 40), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (200, 40), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (240, 40), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (280, 40), 5, 0)

    pygame.draw.circle(DISPLAYSURF, WHITE, (140, 60), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (180, 60), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (220, 60), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (260, 60), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (300, 60), 5, 0)

    pygame.draw.circle(DISPLAYSURF, WHITE, (120, 80), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (160, 80), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (200, 80), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (240, 80), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (280, 80), 5, 0)

    pygame.draw.circle(DISPLAYSURF, WHITE, (140, 100), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (180, 100), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (220, 100), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (260, 100), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (300, 100), 5, 0)

    pygame.draw.circle(DISPLAYSURF, WHITE, (120, 120), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (160, 120), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (200, 120), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (240, 120), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (280, 120), 5, 0)

    pygame.draw.circle(DISPLAYSURF, WHITE, (140, 140), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (180, 140), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (220, 140), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (260, 140), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (300, 140), 5, 0)

    pygame.draw.circle(DISPLAYSURF, WHITE, (120, 160), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (160, 160), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (200, 160), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (240, 160), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (280, 160), 5, 0)

    pygame.draw.circle(DISPLAYSURF, WHITE, (140, 180), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (180, 180), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (220, 180), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (260, 180), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (300, 180), 5, 0)

    pygame.draw.circle(DISPLAYSURF, WHITE, (120, 200), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (160, 200), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (200, 200), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (240, 200), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (280, 200), 5, 0)

    pygame.draw.circle(DISPLAYSURF, WHITE, (140, 220), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (180, 220), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (220, 220), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (260, 220), 5, 0)
    pygame.draw.circle(DISPLAYSURF, WHITE, (300, 220), 5, 0)


def changeBackgroundAnimation(animationSpeed=40):
    global bgColor
    newBgColor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    newBgSurf = pygame.Surface((WINDOWWIDTH, WINDOWHEIGHT))
    newBgSurf = newBgSurf.convert_alpha()
    r, g, b = newBgColor
    for alpha in range(0, 255, animationSpeed):  # animation loop
        checkForQuit()
        DISPLAYSURF.fill(bgColor)

        newBgSurf.fill((r, g, b, alpha))
        DISPLAYSURF.blit(newBgSurf, (0, 0))

        drawButtons()  # redraw the buttons on top of the tint

        pygame.display.update()
        FPSCLOCK.tick(FPS)
    bgColor = newBgColor


def gameOverAnimation(color=WHITE, animationSpeed=50):
    # play all beeps at once, then flash the background
    BEEP5 = pygame.mixer.Sound('GameOver.ogg')
    origSurf = DISPLAYSURF.copy()
    flashSurf = pygame.Surface(DISPLAYSURF.get_size())
    flashSurf = flashSurf.convert_alpha()
    BEEP5.play().set_volume(10000)
    r, g, b = color
    for i in range(3):  # do the flash 3 times
        for start, end, step in ((0, 255, 1), (255, 0, -1)):
            # The first iteration in this loop sets the following for loop
            # to go from 0 to 255, the second from 255 to 0.
            for alpha in range(start, end, animationSpeed * step):  # animation loop
                # alpha means transparency. 255 is opaque, 0 is invisible
                checkForQuit()
                flashSurf.fill((r, g, b, alpha))
                DISPLAYSURF.blit(origSurf, (0, 0))
                DISPLAYSURF.blit(flashSurf, (0, 0))
                drawButtons()
                pygame.display.update()
                FPSCLOCK.tick(FPS)


def getButtonClicked(x, y):
    if YELLOWRECT.collidepoint((x, y)):
        return YELLOW
    elif BLUERECT.collidepoint((x, y)):
        return BLUE
    elif REDRECT.collidepoint((x, y)):
        return RED
    elif GREENRECT.collidepoint((x, y)):
        return GREEN
    return None


if __name__ == '__main__':
    main()