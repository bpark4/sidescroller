import pygame,random
from pygame.locals import *

class Enviro:

    # Class for level environment
    # includes level floor and enemies
    # Randomly generates level to the right
    # Loops level to the left
    floor = []

    
    def __init__(self,wWidth = 800,wHeight = 600,diff = 0):
        #list of enemies (all Enemy objects)
        self.enemies = []
        # width/height of enemies
        self.enemy_size = 32
        # requires algorithm to generate jumper enemy
        self.gen_jump = False
        # next floor height
        self.next = 500
        # difficulty setting (0-easy,1-medium,2-hard)
        self.diff = diff
        # change bounds of length of platforms based on difficulty
        if self.diff == 0:
            self.length = random.randint(0,800)
        elif self.diff == 1:
            self.length = random.randint(0,500)
        else:
            self.length = random.randint(0,200)
        #counter for the length of platform
        self.len_count = 0
        # y values for the floor
        self.floor = [[500]]*int(wWidth)
        # window width and height
        self.width = wWidth
        self.height = wHeight
        # number of ghosts to pass before level ends
        self.count_to_win = 5
        # complete level 3 to win
        self.win = False

    def on_render(self,screen):
        # render floor and enemies
        for i in range(len(self.floor)):
            for j in range(len(self.floor[i])):
                rect = pygame.Rect(i,self.floor[i][j],1,random.randint(1,25))
                pygame.draw.rect(screen,pygame.Color('white'),rect)
                for enemy in self.enemies:
                    enemy.on_render(screen)

    def shift(self,right):
        # shifts screen based on if the player is going right or not
        if right:
            shifter = self.floor[1:]
            # if end of platform length is reached generate new platform height
            # and length
            if self.len_count <= self.length:
                shifter.append([self.next])
                self.len_count += 1
            else:
                if self.next-150>150:
                    self.next = random.randint(self.next-150,self.height)
                else:
                    self.next = random.randint(self.next,self.height)
                if self.diff == 0:
                    self.length = random.randint(0,800)
                elif self.diff == 1:
                    self.length = random.randint(0,500)
                else:
                    self.length = random.randint(0,200)
                self.len_count = 0
                shifter.append([self.next])
                
            alpha = random.uniform(0,1)*80
            #number of ghosts allowed on screen at once (changes per difficulty)
            num_ghosts = 1
            # number less than delta generates ghost (changes per difficulty)
            delta = 0.1
            if self.diff == 1:
                delta = 0.2
                num_ghosts = 3
            elif self.diff == 2:
                delta = 0.5
                num_ghosts = 4

            # if level can fit more ghosts and alpha is under delta, generate ghost
            if len(self.enemies)<num_ghosts:
                if alpha < delta:
                    # 50% chance of generating a jumper ghost
                    if random.uniform(0,1)*80 < 40 or self.gen_jump:
                        self.enemies.append(Enemy(self.width,self.next-self.enemy_size,j = True))
                        if self.gen_jump:
                            self.gen_jump = False
                    else:
                        self.enemies.append(Enemy(self.width,self.next-self.enemy_size,j = False))

            # moves ghosts and gets rid of ghosts that the player has passed
            e = [x for x in self.enemies]
            for enemy in range(len(self.enemies)):
                if self.enemies[enemy].get_x()< -32:
                    e[enemy] = None
                    self.count_to_win -= 1
                else:
                    self.enemies[enemy].move_left(1)
            self.enemies = [x for x in e if not x==None]
        else:
            # if going backwards loop the map
            shifter = self.floor[0:-1]
            shifter.insert(0,self.floor[-1])
            # remove enemy if going backwards, but if it is a jumper
            # require next enemy to be a jumper
            e = [x for x in self.enemies]
            for enemy in range(len(self.enemies)):
                if self.enemies[enemy].get_x() > self.width:
                    if e[enemy].is_jumper():
                        self.gen_jump = True
                    e[enemy] = None
                else:
                    self.enemies[enemy].move_right(1)
            self.enemies = [x for x in e if not x==None]
        #print(len(shifter))
        # replaces floor with shifted floor
        self.floor = shifter
    
    def next_level(self):
        # checks if you've achieved the next level
        if self.count_to_win<=0 and self.diff<2:
            # if completed starting levels go to next
            self.diff+=1
            self.count_to_win=5*self.diff
            return True
        elif self.count_to_win<=0 and self.diff>=2:
            # if completed final level you win
            self.win = True
            return False
        else:
            return False

    def get_floor(self,x,y,w,h):
        # returns the height of floor directly below object
        below = []
        for us in self.floor[x:x+w]:
            for unit in us:
                # if object is on floor return floor
                if y==unit:
                    return unit-h
                # if floor is below object add to list
                elif y < unit:
                    below.append(unit)
        
        if len(below) == 0:
            return 0
        else:
            #print(below)
            # return the closest floor below player
            return min(below)-h
        
    def get_enemies(self):
        # return enemies list
        return self.enemies

    def get_level(self):
        # returns level number
        return self.diff
    
    def won(self):
        # checks if you've won
        return self.win

class Player:
    # class for player, tracks player jumping and step up feature
    # x and y coord for player, width and height of player
    x = 280
    y = 10
    width = 32
    height = 32

    def __init__(self, ww, wh):
        # is player jumping
        self.jump = True
        # timer to time jump
        self.jump_timer = 0
        # player sprite
        self.player = pygame.image.load(r'./stand.png')
        self.sprite_counter = 0
        # y value of floor below player
        self.floor = 0
        # window width
        self.windowW = ww
        # window height
        self.windowH = wh
        # previous floor player was over
        self.last_floor = 0
        # number of lives
        self.lives = 3
        # whether or not player is off the ground
        self.off = True
        # is the game over
        self.isOver = False

    def move(self):
        # player movement
        # if next floor is within step up range, step up
        if self.last_floor-self.floor<int(self.height+2) and self.last_floor-self.floor>0 and self.last_floor==self.y:
            self.y -= self.last_floor-self.floor
        # if player is above or below a floor
        # check if it is jumping
        # if jumping timer has not expired go up
        # if jumping timer expired go back down
        if self.y<self.floor or self.y>self.floor:
            if self.jump and self.jump_timer>0:
                self.y -= 1
                self.jump_timer -= 1
            else:
                self.y += 1
            self.off = True
        else:
            # if on floor and jumping, keep jumping
            # if on floor and not jumping, change jump false
            self.off = False
            if self.jump_timer==0:
                self.jump = False
            else:
                self.y -= 1
                self.jump_timer -=1

    def moving_left(self):
        # changes sprite if moving left to imitate walking
        if self.sprite_counter < 30:
            self.player = pygame.image.load(r'./RL.png')
            self.sprite_counter += 1
        else:
            self.player = pygame.image.load(r'./RL1.png')
            self.sprite_counter += 1
        if self.sprite_counter > 60:
            self.sprite_counter = 0

    def moving_right(self):
        # changes sprite if moving right to imitate walking
        if self.sprite_counter < 30:
            self.player = pygame.image.load(r'./RR1.png')
            self.sprite_counter += 1
        else:
            self.player = pygame.image.load(r'./RR2.png')
            self.sprite_counter += 1
        if self.sprite_counter > 60:
            self.sprite_counter = 0

    def jump_now(self):
        # begins a jumping sequence
        if not self.jump and not self.off:
            self.jump = True
            self.jump_timer = 150
            self.y-=1

    def on_render(self,screen):
        # draw player based on player position
        screen.blit(self.player, (self.x,self.y))
        # change player to standing by default
        self.player = pygame.image.load(r'./stand.png')
        #pygame.display.flip()

    def over(self):
        # check if game is over
        return self.isOver
                    
    def set_floor(self,f):
        # sets the next floor below player
        self.last_floor = self.floor
        self.floor = f

    def end_game(self):
        # ends the game
        self.isOver = True

    def get_x(self):
        # return player x coord
        return self.x

    def get_y(self):
        # return player y coord
        return self.y

    def get_w(self):
        # return player width
        return self.width

    def get_h(self):
        # return player height
        return self.height

    def lose_life(self):
        # player loses a life if lives are left
        # if no lives left end game
        if self.lives > 0:
            self.lives -= 1
        else:
            self.end_game()

    def restart(self):
        # restarts player to top of screen
        self.y = 10

    def get_lives(self):
        # returns number of lives left
        return self.lives

class Enemy:

    # enemy class, controls location and whether an enemy is a jumper
    # if jumper controls jumping
    def __init__(self,x=150,y=150,j = False):
        # x and y coord of enemy
        self.x = x
        self.y = y
        # original y coord of enemy
        self.og_y = y
        # width and height of enemy
        self.w = 32
        self.h = 32
        # is the enemy a jumper
        self.jumper = j
        # timer to space out jumping of enemy
        self.jumper_count = 600
        # is the enemy actively jumping
        self.jumping = False
        # sprite of enemy(ghost)
        self.ghost = pygame.image.load(r'./ghost.jpg')

    def on_render(self,screen):
        # show ghost on screen and execute jumping if jumper
        screen.blit(self.ghost, (self.x,self.y))
        if self.jumper:
            self.jump()

    def is_jumper(self):
        # return whether the enemy is a jumper
        return self.jumper

    def reset(self):
        # resets enemy to left side of screen
        self.x = -32

    def move_right(self,step):
        # move enemy right
        self.x += step

    def move_left(self,step):
        # move enemy left
        self.x -= step

    def jump(self):
        # initiates jumping sequence
        # if on ground and jumper then start jumping
        # if 150 pixels off the ground and jumper stop jumping
        if self.y == self.og_y and self.jumper:
            self.jumping = True
        elif self.y <= self.og_y - 150 and self.jumper:
            self.jumping = False

        # increments jumping based on count
        if self.jumping:
            if self.jumper_count <= 0:
                self.y -= 1
                self.jumper_count = 600
            else:
                self.jumper_count -= 1
        else:
            if self.jumper_count <= 0:
                self.y += 1
                self.jumper_count = 600
            else:
                self.jumper_count -= 1

    def get_x(self):
        # return x coord of enemy
        return self.x

    def get_y(self):
        # return y coord of enemy
        return self.y

    def get_w(self):
        # return width of enemy
        return self.w

    def get_h(self):
        # return height of enemy
        return self.h

class Hud:
    
    # class for the heads up display, displays text when needed and lives
    def __init__(self,screen = None,ww=800,wh=600):
        # screen to write to
        self.screen = screen
        # window width and height
        self.windowWidth = ww
        self.windowHeight = wh

    def instructions(self):
        # alert player of instructions
        pygame.font.init()
        end = pygame.font.SysFont('Comic Sans MS', 30)
        textsurface = end.render('Try right and up arrow keys', True,(255,255,255))
        self.screen.blit(textsurface,(self.windowWidth/4+100,self.windowHeight/4-100))

    def next_level(self):
        # alert player that they have entered the next level
        pygame.font.init()
        end = pygame.font.SysFont('Comic Sans MS', 30)
        textsurface = end.render('Next Level', True,(255,255,255))
        self.screen.blit(textsurface,(self.windowWidth/4+100,self.windowHeight/4))
        pygame.display.flip()

    def game_over(self):
        # alert player that the game is over
        pygame.font.init()
        end = pygame.font.SysFont('Comic Sans MS', 30)
        textsurface = end.render('Game Over', True,(255,255,255))
        self.screen.blit(textsurface,(self.windowWidth/4+100,self.windowHeight/4))
        pygame.display.flip()

    def win(self):
        # alert player that they have won
        pygame.font.init()
        end = pygame.font.SysFont('Comic Sans MS', 30)
        textsurface = end.render('YOU WIN!', True,(255,255,255))
        self.screen.blit(textsurface,(self.windowWidth/4+100,self.windowHeight/4))
        pygame.display.flip()

    def render_lives(self,lives):
        # draw life counter on screen
        for life in range(lives):
            rect = pygame.Rect(40*(life+1)+30,30,32,32)
            pygame.draw.rect(self.screen,pygame.Color('white'),rect)
 
class App:

    # Grand master app class

    # window width and height
    windowWidth = 800
    windowHeight = 600

    def __init__(self):
        # first init to start everything
        # whether or not to keep running app
        self._running = True
        # surface to display game on
        self._display_surf = None
        # environment
        self.enviro = None
        # clock
        self.clock = None
        # player
        self.player = None
        # big moon
        self.enemy = None
        # heads up display
        self.hud = None

    def on_init(self):
        # start pygame
        pygame.init()
        # show display
        self._display_surf = pygame.display.set_mode((self.windowWidth,self.windowHeight))
        # run app
        self._running = True
        # starting environment
        self.enviro = Enviro(self.windowWidth,self.windowHeight,diff = 0)
        # starting player
        self.player = Player(self.windowWidth,self.windowHeight)
        # clock
        self.clock = pygame.time.Clock()
        # heads up display
        self.hud = Hud(screen = self._display_surf)
        # big moon
        self.enemy = pygame.image.load(r'./big_boy.png')

    def on_render(self):
        # show all parts of screen
        # clean slate
        self._display_surf.fill((32,32,32))
        # show player
        self.player.on_render(self._display_surf)
        # show environment
        self.enviro.on_render(self._display_surf)
        # show moon
        self._display_surf.blit(self.enemy,(150,150))
        # show heads up display
        self.hud.render_lives(self.player.get_lives())
        # render instructions if first level
        if(self.enviro.get_level() == 0):
            self.hud.instructions()
        # wait
        self.clock.tick(200)
        # flip screen
        pygame.display.flip()

    def hit_enemy(self):
        # checks if player has hit an enemy
        # gets enemies from environment
        enemies = self.enviro.get_enemies()
        # checks all enemies to see if player overlaps
        for e in enemies:
            if (self.player.get_x()>=e.get_x() and self.player.get_x()<=e.get_x()+e.get_w()) or (self.player.get_x()+self.player.get_w()>=e.get_x() and self.player.get_x()+self.player.get_w()<=e.get_x()+e.get_w()):
                if (self.player.get_y()>=e.get_y() and self.player.get_y()<=e.get_y()+e.get_h()) or (self.player.get_y()+self.player.get_h()>=e.get_y() and self.player.get_y()+self.player.get_h()<=e.get_y()+e.get_h()):                 
                    # if player has hit enemy lose a life and restart position
                    self.player.lose_life()
                    self.player.restart()
                    
    def on_execute(self):
        # if init fails stop running
        if self.on_init() == False:
            self._running = False

        # main loop    
        while( self._running):
            # render everything
            self.on_render()
                
            # prime for next event
            pygame.event.pump()
            # key pressing event
            keys = pygame.key.get_pressed()
            # move player
            self.player.move()
            # set floor of player
            self.player.set_floor(self.enviro.get_floor(self.player.get_x(),self.player.get_y(),self.player.get_w(),self.player.get_h()))

            # if right key pressed shift right
            if(keys[K_RIGHT]):
                self.enviro.shift(True)
                self.player.moving_right()
            # if left key pressed shift left
            if(keys[K_LEFT]):
                self.enviro.shift(False)
                self.player.moving_left()
            # if up pressed player jumps
            if(keys[K_UP]):
                self.player.jump_now()

            # if player falls off screen lose a life and reset position
            if self.player.get_y() > self.windowHeight:
                self.player.lose_life()
                self.player.restart()

            # checks if player runs into enemy
            self.hit_enemy()

            # if game is over on player side stop running and show game over sequence
            if self.player.over():
                self._running = False
                self.hud.game_over()
                self.clock.tick(0.3)

            # if next level is achieved show next level sequence
            if self.enviro.next_level():
                self.hud.next_level()
                self.clock.tick(0.3)

            # if player has won the game show winning sequence
            if self.enviro.won():
                self._running = False
                self.hud.win()
                self.clock.tick(0.3)

            # stop playing by hitting escape
            if(keys[K_ESCAPE]):
                self._running = False

            # work around way to get window close button to work
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
            

        # quit if game is over
        pygame.quit()

if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()
