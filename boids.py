import pygame
import random
import math




SCREEN_X = 1024
SCREEN_Y = 768
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (50,50,255)
YELLOW = (255,255,0)
RED = (255,0,0)

fps = 50


pygame.init()
screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
clock = pygame.time.Clock()
pygame.display.set_caption("Erling Boid")

BOID_SIZE = 5
HOIK_SIZE = 3

NR_OBJECTS = 3
NR_BOIDS = 50
NR_HOIKS = 2

# Inspiration from http://www.red3d.com/cwr/boids/
AVOIDANCE_DIST = 60
SEPERATION_DIST = 5
ALIGNMENT_DIST = 50
COHESION_DIST = 60

# En klasse for å konstruere sprite
class Draw_Object(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([self.size_x, self.size_y])
        self.image.fill(self.colour)
        self.rect = self.image.get_rect()
        self.rect.x = random.uniform(0, SCREEN_X-self.size_x)
        self.rect.y = random.uniform(0, SCREEN_Y-self.size_y)
        self.turn_rate = 0.35
        self.max_speed = 4
        self.min_speed = 3
        self.speed_x = random.randrange(-3,3,1)
        self.speed_y = random.randrange(-3,3,1)
        if (self.speed_x == 0 or self.speed_x == 0):
            self.speed_x, self.speed_y = 1,1
        self.neighbour_group = 0
        self.x_rate = 0
        self.y_rate = 0
        

        
# For obstacle objekter
class Obstacle_Object(Draw_Object):
    def __init__(self):
        self.size_x = random.uniform(0, 200)
        self.size_y = random.uniform(0, 200)
        self.colour = YELLOW
        super().__init__()
        
        
# For flying_object, har flere parametere og funksjoner       
class Flying_Object(Draw_Object):
    def __init__(self):
        self.size_x = BOID_SIZE
        self.size_y = BOID_SIZE
        self.colour = BLUE
        super().__init__()
        self.group = flying_group
        
    # Avoiding obstacles on the screen
    def avoid_obstacle(self, obstacle_group):
        for obstacle in obstacle_group:
            if self.rect.centerx in range(obstacle.rect.x-AVOIDANCE_DIST, obstacle.rect.x+obstacle.rect.width+AVOIDANCE_DIST):
                if self.rect.centery in range(obstacle.rect.y-AVOIDANCE_DIST, obstacle.rect.y+obstacle.rect.height+AVOIDANCE_DIST):
                    if self.rect.centerx < obstacle.rect.left:
                        self.speed_x += -self.turn_rate
                    if self.rect.centerx > obstacle.rect.right:
                        self.speed_x += self.turn_rate
                    if self.rect.centery < obstacle.rect.top:
                        self.speed_y += -self.turn_rate
                    if self.rect.centery > obstacle.rect.bottom:
                        self.speed_y += self.turn_rate  
                        
      
    def obstacle_clip(self, obstacle_group):
        obstacle_list = pygame.sprite.spritecollide(self, obstacle_group,False)
        for obstacle in obstacle_list:
            
            if self.rect.centerx < obstacle.rect.left:
                self.speed_x *= -1
                self.rect.centerx = obstacle.rect.left - self.size_x
                
            if self.rect.centerx > obstacle.rect.right:
                self.speed_x *= -1
                self.rect.centerx = obstacle.rect.right + self.size_x
                
            if self.rect.centery < obstacle.rect.top:
                self.speed_y *= -1
                self.rect.centery = obstacle.rect.top - self.size_y
                
            if self.rect.centery > obstacle.rect.bottom:
                self.speed_y *= -1
                self.rect.centery = obstacle.rect.bottom + self.size_y
                
    # Avoidance of walls around the screen algorithm            
    def avoid_wall(self):         
        # Unngår skjerm boundries 
        if self.rect.centerx < 0 + AVOIDANCE_DIST:
            self.speed_x += self.turn_rate            
        if self.rect.centerx > SCREEN_X - AVOIDANCE_DIST:
            self.speed_x += -self.turn_rate
        if self.rect.centery < 0 + AVOIDANCE_DIST:
            self.speed_y += self.turn_rate
        if self.rect.centery > SCREEN_Y - AVOIDANCE_DIST:
            self.speed_y += -self.turn_rate
         
    # If crash in wall will put back on screen (not flying/clipping off)  
    def wall_clip(self):
        if self.rect.centerx < 0:
            self.rect.centerx = 0
            self.speed_x *= -1
        if self.rect.centerx > SCREEN_X:
            self.rect.centerx = SCREEN_X
            self.speed_x *= -1
        if self.rect.centery < 0:
            self.rect.centery = 0
            self.speed_y *= -1
        if self.rect.centery > SCREEN_Y:
            self.rect.centerx = SCREEN_X
            self.speed_y *= -1
            
    # Avoiding other flying objects
    def separation(self, fly_obj_list):
        for fly_obj in fly_obj_list:
            if fly_obj is not self:
                if self.rect.centerx in range(fly_obj.rect.left - AVOIDANCE_DIST, fly_obj.rect.right + AVOIDANCE_DIST):
                    if self.rect.centery in range(fly_obj.rect.top - AVOIDANCE_DIST, fly_obj.rect.bottom + AVOIDANCE_DIST): 
                        if self.rect.centerx < fly_obj.rect.left:
                            self.speed_x += -0.05   
                        if self.rect.centerx > fly_obj.rect.right:
                            self.speed_x += 0.05
                        if self.rect.centery < fly_obj.rect.top:
                            self.speed_y += -0.05
                        if self.rect.centery > fly_obj.rect.bottom:
                            self.speed_y += 0.05
    
    
    # Function that mover trying to get the same speed as its neighbours
    def alignment(self, fly_obj_list):
        for fly_obj in fly_obj_list:
            if fly_obj is not self:
                if fly_obj.rect.centerx in range(self.rect.left - ALIGNMENT_DIST, self.rect.right + ALIGNMENT_DIST):
                    if fly_obj.rect.centery in range(self.rect.top - ALIGNMENT_DIST, self.rect.bottom + ALIGNMENT_DIST):        
                        self.x_rate += fly_obj.speed_x
                        self.y_rate += fly_obj.speed_y
                        self.neighbour_group += 1
        if self.neighbour_group != 0:
            avg_x = self.x_rate / self.neighbour_group
            avg_y = self.y_rate / self.neighbour_group
            self.speed_x += avg_x * 0.01
            self.speed_y += avg_y * 0.01
        self.nuller()
            
    # Function that mover trying to get the average position as its neighbours
    def cohesion(self, fly_obj_list):
        for fly_obj in fly_obj_list:
            if fly_obj is not self:
                if fly_obj.rect.centerx in range(self.rect.left - COHESION_DIST, self.rect.right + COHESION_DIST):
                    if fly_obj.rect.centery in range(self.rect.top - COHESION_DIST, self.rect.bottom + COHESION_DIST):   
                        self.x_rate += fly_obj.rect.centerx  
                        self.y_rate += fly_obj.rect.centery
                        self.neighbour_group+= 1 
        if self.neighbour_group != 0:
            avg_x = self.x_rate / self.neighbour_group 
            avg_y = self.y_rate / self.neighbour_group
            self.speed_x += (avg_x - self.rect.centerx) * 0.01 
            self.speed_y += (avg_y - self.rect.centery) * 0.01
        self.nuller()
        
        
    # Making that flying objects don't go past a max value
   
# Speed check made by https://vanhunteradams.com/Pico/Animal_Movement/Boids-algorithm.html   
    def speed_check(self):  
        speed = math.sqrt(pow(self.speed_x ,2) + pow(self.speed_y,2))
        if speed > self.max_speed:
            self.speed_x = (self.speed_x/speed) * self.max_speed
            self.speed_y = (self.speed_y/speed) * self.max_speed
        if speed < self.min_speed:
            self.speed_x = (self.speed_x/speed) * self.min_speed
            self.speed_y = (self.speed_y/speed) * self.min_speed
            
        
        
        # max speed for x 
        # if abs(self.speed_x) > self.max_speed:
        #     if self.speed_x > 0:
        #         self.speed_x = self.max_speed
        #     if self.speed_x < 0:
        #         self.speed_x = -self.max_speed
                
        # # max speed for y
        # if abs(self.speed_y) > self.max_speed:
        #     if self.speed_y > 0:
        #         self.speed_y = self.max_speed
        #     if self.speed_y < 0:
        #         self.speed_y = -self.max_speed
                
        # if abs(self.speed_y) < 1 and abs(self.speed_x < 1):
        #     if abs(self.speed_y) > abs(self.speed_x):
        #         if self.speed_y > 0:
        #             self.speed_y = 1
        #         else:
        #             self.speed_y = -1
        #     else:
        #         if self.speed_x > 0:
        #             self.speed_x = 1
        #         else:
        #             self.speed_x = -1
    
    def nuller(self):
        self.x_rate = 0
        self.y_rate = 0
        self.neighbour_group = 0
    
    def update(self):
        self.alignment(self.group)
        self.separation(self.group)
        self.cohesion(self.group)
        
        self.avoid_wall()
        self.avoid_obstacle(obstacle_group)
        self.obstacle_clip(obstacle_group)
        self.wall_clip()
        
        
        self.speed_check()
        self.rect.centerx += self.speed_x
        self.rect.centery += self.speed_y
    

                

obstacle_group = pygame.sprite.Group()
flying_group = pygame.sprite.Group()
for _ in range(NR_OBJECTS):
    obstacle_group.add(Obstacle_Object())
for _ in range (NR_BOIDS):
    flying_group.add(Flying_Object())
for _ in range (NR_HOIKS):
    flying_group.add(Flying_Object())
    
while True:
    event = pygame.event.poll()

    if event.type == pygame.QUIT:
        break
    if event.type == pygame.K_ESCAPE: # Funker ikke
        break
    
    screen.fill(BLACK)
    obstacle_group.update()
    obstacle_group.draw(screen)
    flying_group.update()
    flying_group.draw(screen)
    pygame.display.update()
    pygame.display.flip()
    clock.tick(fps)
    # input()
    
    
        