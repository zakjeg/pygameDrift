import pygame
import math

pygame.init()

WIDTH, HEIGHT = 1280, 720
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255,0,0)
CAR_WIDTH, CAR_HEIGHT = 50, 25
ARROW_COLOR = (255, 0, 0)  

display = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

pygame.mixer.init()
startup_sound = pygame.mixer.Sound('assets/startup.wav')
idle_sound = pygame.mixer.Sound('assets/idle.wav')
power_sound = pygame.mixer.Sound('assets/power.wav')
tyre_sound = pygame.mixer.Sound('assets/tyre.wav')
tyre_playing = False  




def rotate_center(image, angle, x, y):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=(x, y))
    return rotated_image, new_rect

def draw_grid(screen, grid_size=40, color=(200, 200, 200)): 
    for x in range(0, WIDTH, grid_size):
        pygame.draw.line(screen, color, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, grid_size):
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = 0
        self.max_speed = 5
        self.friction = 0.02
        self.turn_speed = 2
        self.drift_factor = 5
        self.rotation_speed = 0  
        self.rotation_deceleration = 0.05
        self.direction_angle=0

        self.image = pygame.Surface((CAR_WIDTH, CAR_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(self.image, BLACK, (0, 0, CAR_WIDTH, CAR_HEIGHT))

    def draw_movement_direction(self, screen):
        if self.velocity.length() > 0.1:
            direction = self.velocity.normalize()

            angle = math.degrees(math.atan2(direction.y, direction.x))
            
            max_arrow_length = 50
            line_length = max_arrow_length * (self.velocity.length() / self.max_speed)
            
            arrowhead_length = max(5, line_length * 0.3) 
            arrowhead_width = max(3, line_length * 0.2)
            
            end_x = self.x + direction.x * line_length
            end_y = self.y + direction.y * line_length
            
            pygame.draw.line(screen, ARROW_COLOR, (self.x, self.y), (end_x, end_y), 3)
            
            left_wing = pygame.Vector2(-direction.y, direction.x) * arrowhead_width
            right_wing = pygame.Vector2(direction.y, -direction.x) * arrowhead_width
            arrow_tip = pygame.Vector2(end_x, end_y)
            left_tip = arrow_tip - (direction * arrowhead_length) + left_wing
            right_tip = arrow_tip - (direction * arrowhead_length) + right_wing
            
            pygame.draw.polygon(screen, ARROW_COLOR, [arrow_tip, left_tip, right_tip])

            self.direction_angle = angle
            return angle
        return 0

    def get_forward_vector(self):
        rad = math.radians(self.angle)
        return pygame.Vector2(math.cos(rad), -math.sin(rad))

    def get_lateral_velocity(self):
        right_normal = pygame.Vector2(-self.velocity.y, self.velocity.x)
        return right_normal * self.velocity.dot(right_normal) / (right_normal.length() if right_normal.length() > 0 else 1)
    
    def update(self, keys):

        global tyre_playing
        if keys[pygame.K_w]:
            self.acceleration = 0.2
        elif keys[pygame.K_s]:
            self.acceleration = -0.1
        else:
            self.acceleration = 0

        self.velocity += self.get_forward_vector() * self.acceleration
        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)
        self.velocity *= (1 - self.friction)
        
        if self.velocity.length() > 0.2:
            if keys[pygame.K_a]:
                self.rotation_speed = self.turn_speed * (self.velocity.length() / self.max_speed)
            elif keys[pygame.K_d]:
                self.rotation_speed = -self.turn_speed * (self.velocity.length() / self.max_speed)
            else:
                if self.rotation_speed > 0:
                    self.rotation_speed -= self.rotation_deceleration
                    if self.rotation_speed < 0:
                        self.rotation_speed = 0
                elif self.rotation_speed < 0:
                    self.rotation_speed += self.rotation_deceleration
                    if self.rotation_speed > 0:
                        self.rotation_speed = 0
        else:
            self.rotation_speed = 0

        self.angle += self.rotation_speed
        
        lateral_velocity = self.get_lateral_velocity()
        self.velocity -= lateral_velocity * self.drift_factor
        
        self.x += self.velocity.x
        self.y += self.velocity.y
        
        if self.velocity.length() > 0.1 and abs(self.angle - self.direction_angle) > 5:
            if not tyre_playing:
                tyre_sound.play(-1)  
                tyre_playing = True
        else:
            if tyre_playing:
                tyre_sound.stop()
                tyre_playing = False
        
        if self.x < 0:
            self.x = 0
        elif self.x > WIDTH:
            self.x = WIDTH
        
        if self.y < 0:
            self.y = 0
        elif self.y > HEIGHT:
            self.y = HEIGHT
        
    def draw(self, screen):
        movement_angle = -self.draw_movement_direction(screen)

        rotated_image, rect = rotate_center(self.image, self.angle, self.x, self.y)
        screen.blit(rotated_image, rect.topleft)

        font = pygame.font.SysFont('Arial', 24)
        angle_text = font.render(f"Angle: {self.angle:.2f}", True, (0, 0, 0))
        screen.blit(angle_text, (10, 10))  

        sinText = font.render(f"Sin(alfa): {(math.sin(math.radians(self.angle)))}", True, (0,0,0))
        screen.blit(sinText,(10,60))
        cosText = font.render(f"Cos(alfa): {(math.cos(math.radians(self.angle)))}", True, (0,0,0))
        screen.blit(cosText,(10,120))
        wheel_size = (10, 5)  
        wheel_offset = 0  
        backWheelOfset=2

        #prednja desna guma
        #top_center_x = self.x  + (math.cos(math.radians(self.angle))*(CAR_WIDTH/2)) - (math.sin(math.radians(self.angle))*(CAR_HEIGHT/2)) 
        #top_center_y = self.y + (math.cos(math.radians(self.angle))*(CAR_HEIGHT/2))
        top_center_x=self.x + math.cos(math.radians(self.angle))*CAR_WIDTH/2.5 - math.sin(math.radians(self.angle))*CAR_HEIGHT/2.5
        top_center_y=self.y - math.cos(math.radians(self.angle))*CAR_HEIGHT/2.5 - math.sin(math.radians(self.angle))*(CAR_WIDTH/2.5)
        wheel1 = pygame.Surface(wheel_size, pygame.SRCALPHA)
        pygame.draw.rect(wheel1, RED, (0, 0, *wheel_size))
        wheel1, rect1 = rotate_center(wheel1, movement_angle, top_center_x, top_center_y)
        screen.blit(wheel1, rect1)
        
        #prednja leva guma
        bottom_center_x = self.x  + math.cos(math.radians(self.angle))*CAR_WIDTH/2.5 + math.sin(math.radians(self.angle))*CAR_HEIGHT/2.5
        bottom_center_y = self.y + math.cos(math.radians(self.angle))*CAR_HEIGHT/2.5 - math.sin(math.radians(self.angle))*(CAR_WIDTH/2.5)
        wheel2 = pygame.Surface(wheel_size, pygame.SRCALPHA)
        pygame.draw.rect(wheel2, RED, (0, 0, *wheel_size))
        wheel2, rect2 = rotate_center(wheel2, movement_angle, bottom_center_x, bottom_center_y)
        screen.blit(wheel2, rect2)

        #zadnja leva guma
        top_back_x = self.x - math.cos(math.radians(self.angle)) * CAR_WIDTH / (backWheelOfset+0.5) - math.sin(math.radians(self.angle)) * CAR_HEIGHT / (backWheelOfset)
        top_back_y = self.y - math.cos(math.radians(self.angle)) * CAR_HEIGHT / (backWheelOfset) + math.sin(math.radians(self.angle)) * (CAR_WIDTH / (backWheelOfset+0.5))
        backWheel1 = pygame.Surface(wheel_size, pygame.SRCALPHA)
        pygame.draw.rect(backWheel1, RED, (0, 0, *wheel_size)) 
        backWheel1, rect3 = rotate_center(backWheel1, self.angle, top_back_x, top_back_y)
        screen.blit(backWheel1, rect3)

        #zadnja desna guma
        bottom_back_x = self.x - math.cos(math.radians(self.angle)) * CAR_WIDTH / (backWheelOfset+0.5) + math.sin(math.radians(self.angle)) * CAR_HEIGHT / backWheelOfset
        bottom_back_y = self.y + math.cos(math.radians(self.angle)) * CAR_HEIGHT / backWheelOfset + math.sin(math.radians(self.angle)) * (CAR_WIDTH / (backWheelOfset+0.5))
        backWheel2 = pygame.Surface(wheel_size, pygame.SRCALPHA)
        pygame.draw.rect(backWheel2, RED, (0, 0, *wheel_size))  
        backWheel2, rect4 = rotate_center(backWheel2, self.angle, bottom_back_x, bottom_back_y)
        screen.blit(backWheel2, rect4)



car = Car(WIDTH//2, HEIGHT//2)

startup_sound.play()

startup_finished = False

power_playing = False

running = True
while running:
    clock.tick(60)
    keys = pygame.key.get_pressed()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    car.update(keys)

    if not startup_finished and not pygame.mixer.get_busy():
        startup_finished = True
        idle_sound.play(-1) 

    if keys[pygame.K_w]:
        if not power_playing:
            power_sound.play() 
            power_playing = True
        if pygame.mixer.get_busy():  
            idle_sound.stop() 
    else:
        if power_playing:
            power_sound.stop()  
            power_playing = False
        if not pygame.mixer.get_busy():  
            idle_sound.play(-1)  

    display.fill(WHITE)
    draw_grid(display)
    car.draw(display)
    pygame.display.flip()
    
pygame.quit()
