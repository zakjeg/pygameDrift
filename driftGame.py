import pygame
import math
import os

#kratek opis igre

# ZAČETNI ZASLON
# Ob zagonu igre se prikaže intro zaslon, kjer igralec lahko pritisne gumb Start Game ali katerokoli tipko za začetek igre. Med tem se predvaja uvodna glasba.

# FIZIKA VOZILA IN PREMIKANJE
# Avto pospešuje s tipko W in zavira s S.
# Zasuk krmila se izvaja s A in D, pri čemer se avto lažje obrača pri večjih hitrostih.
# Trenje in driftanje sta simulirana tako, da avto ne spremeni takoj smeri gibanja, temveč obdrži nekaj bočnega drsenja.
# Če se hitrost zmanjša, se zavijanje upočasni, kar doda realizem vožnji.

# ZAZNAVANJE CESTE IN TOČKOVANJE
# Igra preverja, ali je avto na cesti, tako da vzame barvo pod njim in jo primerja z barvo ceste.
# Če je vozilo na cesti, se točke pridobivajo glede na hitrost in kot driftanja. Večji kot driftanja pomeni več točk.
# Če avto zapusti cesto, se točke ne prištevajo.

# ČASOVNA OMEJITEV IN CILJNA ČRTA
# Igra se začne, ko avto prvič prečka ciljno črto.
# Odštevanje traja 60 sekund – igralec mora v tem času nabrati čim več točk.
# Ko čas poteče, se prikaže zaslon z rezultatom in možnostjo ponovnega igranja.

# ZVOČNI UČINKI
# Motorni zvoki se spreminjajo glede na pospeševanje.
# Zvok driftanja se predvaja, če avto drsi pod določenim kotom.
# Glasba igra v ozadju in se prekine, ko je igra končana.

# OPCIJA ZA PONOVNO IGRRANJE
# Po koncu igre lahko igralec pritisne R, da jo začne znova.
# Če pritisne T, se prikaže skriti zaključni zaslon.
# Če igralec ne naredi ničesar, se igra po 30 sekundah avtomatsko zapre.


pygame.init()

# konstante
WIDTH, HEIGHT = 1280, 720
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CAR_WIDTH, CAR_HEIGHT = 50, 25

display = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
timerStarted=False
start_timer = False
time_left = 10  
timer_started_at = None

background = pygame.image.load("assets/theRaceTrack.png").convert_alpha()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
backgroundOverlay = pygame.image.load("assets/theRaceTrackOverlay.png").convert_alpha()
backgroundOverlay = pygame.transform.scale(backgroundOverlay, (WIDTH, HEIGHT))

# Nalaganje zvočnih učinkov
pygame.mixer.init()
startup_sound = pygame.mixer.Sound('assets/startup.wav')
idle_sound = pygame.mixer.Sound('assets/idle.wav')
power_sound = pygame.mixer.Sound('assets/power.wav')
tyre_sound = pygame.mixer.Sound('assets/tyre.wav')
tyre_playing = False
pygame.mixer.music.load('assets/introTrack.wav')


score = 0
score_update_interval = 1000  # 1000ms = 1 sekunda
last_score_update = pygame.time.get_ticks()

def welcome_screen():
    welcome_font = pygame.font.Font("assets/pixelFont.ttf", 60)
    button_font = pygame.font.Font("assets/pixelFont.ttf", 20)

    display.fill(WHITE)

    intro_image = pygame.image.load("assets/introImage.png").convert_alpha()  
    intro_image = pygame.transform.scale(intro_image, (WIDTH, HEIGHT))  
    display.blit(intro_image, (0, 0))  # Prikaz intro slike

    # prikaz naslova
    title_text = welcome_font.render('Welcome to the PoSrek game!', True, BLACK)
    display.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))
    
    # prikaz gumba za začetek
    button_text = button_font.render('Start Game', True, WHITE)
    button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
    pygame.draw.rect(display, (0, 0, 255), button_rect)  # Blue button
    display.blit(button_text, (button_rect.x + 40, button_rect.y + 10))

    # prikaz zaslona
    pygame.display.flip()
    
    # čakanje na klik gumba... (ali tipke)
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    waiting = False  # začni igro if(gumb pritisnjen)

            if event.type == pygame.KEYDOWN:
                waiting = False  # začne igro, če je katerakoli tipka pritisnjena

def is_on_track(car_x, car_y, track_image): 
    if car_x < 0 or car_y < 0 or car_x >= track_image.get_width() or car_y >= track_image.get_height():
        return 0  # vrne 0 če avto ni v okvirju

    track_color = track_image.get_at((int(car_x), int(car_y)))[:3]  # ignorira alfa kanal (iz RGBA dobimo RGB)

    ROAD_COLOR = (150, 150, 150)  # Barva ceste
    WHITE_LINE_COLOR = (255, 255, 255)  # Barva bele črte (bela...)

    TOLERANCE = 10  #Toleranca pri barvah (cesta ni ves čas isto obarvana, vmes so male razlike)

    is_road = all(abs(track_color[i] - ROAD_COLOR[i]) < TOLERANCE for i in range(3))

    is_white_line = all(track_color[i] > 240 for i in range(3))  

    if(is_road or is_white_line):
        output = calculate_score(car.velocity, car.angle, car.direction_angle)
        print(f"score += {output}")
        return output
    
    return 0


def rotate_center(image, angle, x, y):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=(x, y))
    return rotated_image, new_rect

def calculate_score(velocity, angle, movAngle):
    if not is_on_track:
        return 0  # ne šteje če je avto izven ceste
    
    velocity_magnitude = velocity.length()

    # Šteje le če se avto premika
    if velocity_magnitude < 0.1:
        return 0

    #Kot "drifta" vpliva na točkovanje. Bolj kot je avto nagnjen - več točk
    score = (abs(angle - movAngle) +  velocity_magnitude)/2
    return int(score)


#deklaracija razreda avto
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
        pygame.draw.rect(self.image, "darkturquoise", (0, 0, CAR_WIDTH, CAR_HEIGHT))

        # Naloži sliko avtomobila in jo prilagodi
        self.car_sprite = pygame.image.load("assets/SportCar.png").convert_alpha()
        self.car_sprite = pygame.transform.scale(self.car_sprite, (CAR_WIDTH+25, CAR_HEIGHT+12))

    def draw_movement_direction(self, screen):
        if self.velocity.length() > 0.1:
            direction = self.velocity.normalize()

            # izračun kota gibanja
            angle = math.degrees(math.atan2(direction.y, direction.x))
            
            # vektor gibanja iz "barebones" modela igre. (ni prikazan / uporabljen)
            max_arrow_length = 50
            line_length = max_arrow_length * (self.velocity.length() / self.max_speed)
            
            arrowhead_length = max(5, line_length * 0.3) 
            arrowhead_width = max(3, line_length * 0.2)
            
            end_x = self.x + direction.x * line_length
            end_y = self.y + direction.y * line_length
            
            #pygame.draw.line(screen, ARROW_COLOR, (self.x, self.y), (end_x, end_y), 3)
            
            left_wing = pygame.Vector2(-direction.y, direction.x) * arrowhead_width
            right_wing = pygame.Vector2(direction.y, -direction.x) * arrowhead_width
            arrow_tip = pygame.Vector2(end_x, end_y)
            left_tip = arrow_tip - (direction * arrowhead_length) + left_wing
            right_tip = arrow_tip - (direction * arrowhead_length) + right_wing
            
            #pygame.draw.polygon(screen, ARROW_COLOR, [arrow_tip, left_tip, right_tip])

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

        # Pospeševanje in zaviranje
        if keys[pygame.K_w]:
            self.acceleration = 0.08
        elif keys[pygame.K_s]:
            self.acceleration = -0.05
        else:
            self.acceleration = 0

        # Posodobitev hitrosti
        self.velocity += self.get_forward_vector() * self.acceleration
        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)
        self.velocity *= (1 - self.friction)
        
        # zavijanje / krmiljenje
        if self.velocity.length() > 0.2:
            if keys[pygame.K_a]:
                self.rotation_speed = self.turn_speed * (self.velocity.length() / self.max_speed)
            elif keys[pygame.K_d]:
                self.rotation_speed = -self.turn_speed * (self.velocity.length() / self.max_speed)
            else:
                # počasi izniči rotacijo če nobena tipka za krmiljenje (a ali d) ni pritisnjena
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

        # rotacija
        self.angle += self.rotation_speed
        
        # simuliranje drsenja
        lateral_velocity = self.get_lateral_velocity()
        self.velocity -= lateral_velocity * self.drift_factor
        
        # premikanje
        self.x += self.velocity.x
        self.y += self.velocity.y
        
        if self.velocity.length() > 0.3 and abs(self.angle - self.direction_angle) > 5:
            if not tyre_playing:
                tyre_sound.play(-1)  # Play in a loop
                tyre_playing = True
        else:
            if tyre_playing:
                tyre_sound.stop()
                tyre_playing = False
        
        # preverjanje meja igre
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

        font = pygame.font.Font("assets/pixelFont.ttf", 40)

        rotated_car_sprite, car_rect = rotate_center(self.car_sprite, self.angle, self.x, self.y)
        wheel_size = (10, 5)  
        backWheelOfset=2

        # risanje gum

        #prednja desna guma
        #top_center_x = self.x  + (math.cos(math.radians(self.angle))*(CAR_WIDTH/2)) - (math.sin(math.radians(self.angle))*(CAR_HEIGHT/2)) 
        #top_center_y = self.y + (math.cos(math.radians(self.angle))*(CAR_HEIGHT/2))
        top_center_x=self.x + math.cos(math.radians(self.angle))*CAR_WIDTH/2.2 - math.sin(math.radians(self.angle))*CAR_HEIGHT/2.2
        top_center_y=self.y - math.cos(math.radians(self.angle))*CAR_HEIGHT/2.2 - math.sin(math.radians(self.angle))*(CAR_WIDTH/2.2)
        wheel1 = pygame.Surface(wheel_size, pygame.SRCALPHA)
        pygame.draw.rect(wheel1, "gray13", (0, 0, *wheel_size))
        wheel1, rect1 = rotate_center(wheel1, movement_angle, top_center_x, top_center_y)
        screen.blit(wheel1, rect1)
        
        #prednja leva guma
        bottom_center_x = self.x  + math.cos(math.radians(self.angle))*CAR_WIDTH/2.2 + math.sin(math.radians(self.angle))*CAR_HEIGHT/2.2
        bottom_center_y = self.y + math.cos(math.radians(self.angle))*CAR_HEIGHT/2.2 - math.sin(math.radians(self.angle))*(CAR_WIDTH/2.2)
        wheel2 = pygame.Surface(wheel_size, pygame.SRCALPHA)
        pygame.draw.rect(wheel2, "gray13", (0, 0, *wheel_size))
        wheel2, rect2 = rotate_center(wheel2, movement_angle, bottom_center_x, bottom_center_y)
        screen.blit(wheel2, rect2)

        #zadnja leva guma
        top_back_x = self.x - math.cos(math.radians(self.angle)) * CAR_WIDTH / (backWheelOfset+0.5) - math.sin(math.radians(self.angle)) * CAR_HEIGHT / (backWheelOfset)
        top_back_y = self.y - math.cos(math.radians(self.angle)) * CAR_HEIGHT / (backWheelOfset) + math.sin(math.radians(self.angle)) * (CAR_WIDTH / (backWheelOfset+0.5))
        backWheel1 = pygame.Surface(wheel_size, pygame.SRCALPHA)
        pygame.draw.rect(backWheel1, "gray13", (0, 0, *wheel_size))  # Fix: use backWheel1 instead of wheel1
        backWheel1, rect3 = rotate_center(backWheel1, self.angle, top_back_x, top_back_y)
        screen.blit(backWheel1, rect3)

        #zadnja desna guma
        bottom_back_x = self.x - math.cos(math.radians(self.angle)) * CAR_WIDTH / (backWheelOfset+0.5) + math.sin(math.radians(self.angle)) * CAR_HEIGHT / backWheelOfset
        bottom_back_y = self.y + math.cos(math.radians(self.angle)) * CAR_HEIGHT / backWheelOfset + math.sin(math.radians(self.angle)) * (CAR_WIDTH / (backWheelOfset+0.5))
        backWheel2 = pygame.Surface(wheel_size, pygame.SRCALPHA)
        pygame.draw.rect(backWheel2, "gray13", (0, 0, *wheel_size))  # Fix: use backWheel1 instead of wheel1
        backWheel2, rect4 = rotate_center(backWheel2, self.angle, bottom_back_x, bottom_back_y)
        screen.blit(backWheel2, rect4)

        #pravokotnik pod avtom (za debuganje)
        #rotated_image, rect = rotate_center(self.image, self.angle, self.x, self.y)
        #screen.blit(rotated_image, rect.topleft)
        
        #avto nakoncu narišemo "čez" gume
        screen.blit(rotated_car_sprite, car_rect.topleft)




pygame.mixer.music.set_volume(0.3)

pygame.mixer.music.play(-1, 0.0)

welcome_screen()
 

finishLine_x=560
finishLineStart_y=600
finishLineEnd_y=680

car = Car(511, 609)
startup_sound.play()
startup_finished = False
power_playing = False
current_score = 0
running = True
last_time_called = pygame.time.get_ticks()

while running:
    clock.tick(60)
    keys = pygame.key.get_pressed()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    display.blit(background, (0, 0))
    car.update(keys)

    #preveri ali avto prečka ciljno črto
    if not timerStarted and finishLine_x - 5 <= car.x <= finishLine_x + 5:  
        if finishLineStart_y <= car.y <= finishLineEnd_y: 
            timerStarted = True  
            timer_started_at = pygame.time.get_ticks()
            start_timer = True
            current_score=0  # Ponastavi točke na nič ko začnemo štopati

    if start_timer:
        elapsed_time = pygame.time.get_ticks() - timer_started_at
        time_left = max(0, 60 - elapsed_time // 1000)  # Posodobi preostali čas. Nastavi spodnjo mejo na 0
        if time_left == 0:
            final_score_font = pygame.font.Font("assets/pixelFont.ttf", 60)
            final_score_text = final_score_font.render(f"Final Score: {current_score}", True, BLACK)
            display.fill(WHITE)
            display.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 3))
            
            instructions_font = pygame.font.Font("assets/pixelFont.ttf", 40)
            instructions_text = instructions_font.render("Press 'R' to Restart or wait to Quit", True, BLACK)
            display.blit(instructions_text, (WIDTH // 2 - instructions_text.get_width() // 2, HEIGHT // 2))
            pygame.display.flip()

            quit_timer_start = pygame.time.get_ticks()
            waiting_for_restart = True
            secret_end_screen_shown = False
            
            while waiting_for_restart:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting_for_restart = False
                        running = False  

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:

                            current_score = 0
                            time_left = 10
                            car.x, car.y = 511, 609  
                            car.velocity = pygame.Vector2(0, 0)  #
                            car.angle = 0 
                            timerStarted = False
                            timer_started_at = None
                            start_timer = False
                            power_playing = False
                            tyre_playing = False
                            pygame.mixer.music.play(-1, 0.0)  
                            waiting_for_restart = False  
                        elif event.key == pygame.K_t:
                            secret_end_screen = pygame.image.load("assets/secredEndScreen.png")
                            display.fill(WHITE) 
                            display.blit(secret_end_screen, (WIDTH // 2 - secret_end_screen.get_width() // 2, HEIGHT // 3))
                            pygame.display.flip()
                            
                            pygame.time.wait(1000)
                            waiting_for_restart = False
                            running = False  
                        else:
                            waiting_for_restart = False
                            running = False

                if pygame.time.get_ticks() - quit_timer_start >= 30000:  
                    waiting_for_restart = False
                    running = False  


    #urejanje zvočnih efektov
    if not startup_finished and not pygame.mixer.get_busy():
        startup_finished = True
        idle_sound.play(-1) 

    if keys[pygame.K_w]:
        if not power_playing:
            power_sound.play(-1) 
            power_playing = True
        if pygame.mixer.get_busy(): 
            idle_sound.stop() 
    else:
        if power_playing:
            power_sound.stop() 
            power_playing = False
        if not pygame.mixer.get_busy(): 
            idle_sound.play(-1)  

    current_time = pygame.time.get_ticks()

    # Preveri če je sekunda (ali 1000ms) že minilo
    if current_time - last_time_called >= 1000:
        current_score += is_on_track(car.x, car.y, background)
        last_time_called = current_time  # Ponastavi timer


    car.draw(display)
    display.blit(backgroundOverlay, (0, 0))

    font = pygame.font.Font("assets/pixelFont.ttf", 40)

    #timer na vrhu zaslona
    if(timerStarted):
        timer_text = font.render(f"Time Left: {time_left} seconds", True, "dodgerblue4")
        display.blit(timer_text, (400, 10))
        score_text = font.render(f"SCORE : {current_score} ", True, "dodgerblue4")
        display.blit(score_text, (550, 50))
    else:
        timer_text = font.render(f"Cross the finishline to start the game.", True, "dodgerblue4")
        display.blit(timer_text, (250, 50))

    pygame.display.flip()
    

pygame.quit()
