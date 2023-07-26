""" Versión Modificada del Juego Shooter de Mundo Python
"""
# Ctrl + Shift + P > Convert Indentation to Spaces > Enter
import pygame, os, random, time

# --- CONSTANTS --- #

SIZE = (1280, 768)
SCREEN_WIDTH, SCREEN_HEIGHT = SIZE[0], SIZE[1]
screen = pygame.display.set_mode(SIZE)

# Colores
BLACK   = (   0,   0,   0)
WHITE   = ( 255, 255, 255)
GREEN   = (   0, 255,   0)
RED     = ( 255,   0,   0)
BLUE    = (   0,   0, 255)
YELLOW  = ( 244, 221,  63)

# --- IMAGES --- #
bg_img = pygame.image.load("assets/img/background.png").convert()

# Animación

def transform_files(file, colorkey):
    img = pygame.image.load(file).convert()
    img.set_colorkey(colorkey)
    return pygame.transform.scale(img, (70, 70))

animation_explosion = [transform_files(os.path.join("assets/img/explosions", file), BLACK) for file in os.listdir("assets/img/explosions")]

pygame.display.set_caption("Starship Shooter 2023")
pygame.mouse.set_visible(0)
clock = pygame.time.Clock()

# --- Definición de clases --- #

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/img/player.png").convert()
        self.explosion_sound = pygame.mixer.Sound("assets/sounds/player_explosion.mp3")
        self.collision_sound = pygame.mixer.Sound("assets/sounds/player_hit_collision.wav")
        self.image.set_colorkey(BLACK)
        # Obtener el rectángulo del Sprite (x, y, width, height)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed_x = 0
        self.speed_y = 0
        self.life_bar = 100

    def update(self):
        # Las velocidades comienzan en 0
        self.speed_x = 0
        self.speed_y = 0
        # Se crea una lista de las teclas presionas que podemos consultar
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_a]:
            self.speed_x = -5
        if keystate[pygame.K_d]:
            self.speed_x = 5
        if keystate[pygame.K_w]:
            self.speed_y = -5
        if keystate[pygame.K_s]:
            self.speed_y = 5
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        """
        Evitar que la nave salga de la pantalla:
            Se consulta por los lados del sprite y si salen de la pantalla
            Se cambia el valor para que pueda sobresalir levemente
        """
        if self.rect.right > SCREEN_WIDTH + (self.rect.width // 2):
            self.rect.right = SCREEN_WIDTH + (self.rect.width // 2)
        if self.rect.left < 0 - (self.rect.width // 2):
            self.rect.left = 0 - (self.rect.width // 2)
        if self.rect.bottom > SCREEN_HEIGHT + (self.rect.height // 2):
            self.rect.bottom = SCREEN_HEIGHT + (self.rect.height // 2)
        if self.rect.top < 0 - (self.rect.height // 2):
            self.rect.top = 0 - (self.rect.height // 2)

    def shoot(self):
        laser = Laser(self.rect.centerx, self.rect.top)
        laser.laser_sound.play()
        return laser

class Laser(pygame.sprite.Sprite):
# Método constructor de la clase Laser
    def __init__(self, x, y):
        # Llamamos al método super para heredar los métodos y atributos de la super clase Sprite
        super().__init__()
        self.laser_sound = pygame.mixer.Sound("assets/sounds/laser.mp3")
        self.image = pygame.image.load("assets/img/laser.png").convert()
        self.image.set_colorkey(BLACK)
        # Definimos el atributo self.rect que guarda la posición del objeto instanciado
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.centerx = x
        self.speed_y = 10

    # Método para dar movimiento al laser, este mov. es solo en el eje Y
    # Para que sea un mov. asc. se debe restar a la coordenada actual
    def update(self):
        self.rect.y -= self.speed_y
        # Si la parte inferior del sprite es menor a 0 se elimina
        # Al eliminar la instancia se libera memoria
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.image = animation_explosion[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        # Con esta instrucción podemos crear un tiempo de inicio (start time)
        # Para comenzar la animación
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50 # velocidad de la animación

    def update(self):
        # Podemos saber el tiempo transcurrido
        now = pygame.time.get_ticks()
        # Nos permite ir cambiando la imagen
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            center = self.rect.center
            self.image = animation_explosion[self.frame]
            self.rect = self.image.get_rect()
            self.rect.center = center
            self.frame += 1
            if self.frame > len(animation_explosion)-1:
                self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.img_list = os.listdir("assets/img/meteors")
        self.image = pygame.image.load(os.path.join("assets/img/meteors", random.choice(self.img_list))).convert()
        self.explosion = pygame.mixer.Sound("assets/sounds/meteor_explosion.wav")
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        # Comenzamos a generar meteoros desde coordendas Y negativas
        self.rect.y = random.randrange(-140, -100)
        # Su velocidad es positiva por que lo comienzan bajando
        self.speed_y = random.randrange(1, 10)
        # Pueden ir a ambos lados
        self.speed_x = random.randrange(-5, 5)

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        # Hacer que los meteoros vuelvan a aparecer una vez salgan de la screen
        if self.rect.top > SCREEN_HEIGHT + 10 or self.rect.left < -40 or self.rect.right > SCREEN_WIDTH + 22 :
            self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_y = random.randrange(1, 8)

class Game(object):
    def __init__(self):
        self.game_over = False
        self.score = 0
        self.all_sprites_set = pygame.sprite.Group()
        self.player = Player()
        self.all_sprites_set.add(self.player)

        self.meteor_set = pygame.sprite.Group()
        for element in range(8):
            meteor = Meteor()
            self.meteor_set.add(meteor)
            self.all_sprites_set.add(meteor)

        self.laser_set = pygame.sprite.Group()

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True

            if event.type == pygame.MOUSEBUTTONDOWN:
                laser = self.player.shoot()
                self.all_sprites_set.add(laser)
                self.laser_set.add(laser)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                self.pause_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
        return False

    def run_logic(self):
        if not self.game_over:
            self.all_sprites_set.update()

            # --- COLISIONES --- #

            ## meteoros -> lasers
            hits_lasers = pygame.sprite.groupcollide(self.meteor_set, self.laser_set, True, True)
            for hit in hits_lasers:
                self.score += 10
                meteor = Meteor()
                meteor.explosion.play()
                explosion = Explosion(hit.rect.center)
                self.all_sprites_set.add(explosion)
                self.meteor_set.add(meteor)
                self.all_sprites_set.add(meteor)

            ## player -> meteoros
            hits = pygame.sprite.spritecollide(self.player, self.meteor_set, True)
            # Si se acaba la life bar el juego finaliza
            if hits:
                if self.player.life_bar <= 0:
                    f = open('assets/scores.txt', 'a')
                    f.write(str(self.score)+",")
                    f.close()
                    self.player.explosion_sound.play()
                    explosion = Explosion(self.player.rect.center)
                    self.all_sprites_set.add(explosion)
                    self.show_go_screen()
                    self.__init__()
                else:
                    meteor = Meteor()
                    self.meteor_set.add(meteor)
                    self.all_sprites_set.add(meteor)
                    self.player.life_bar -= 25
                    self.player.collision_sound.play()
                    time.sleep(0.5)

    def draw_text(self, surface, text, size, x, y):
        font = pygame.font.SysFont("monospace", size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        surface.blit(text_surface, text_rect)

    def max_score(self) -> int:
        f = open('assets/scores.txt', 'r')
        text = f.read()
        f.close()
        text = list(text)
        text.pop()
        text = "".join(text)
        num_str = text.split(",")
        score = [int(i) for i in num_str]
        return max(score)

    def draw_life_bar(self, surface, life_value, x, y):
        bar_lenght = 100
        bar_height = 20
        fill = (life_value / 100) * bar_lenght
        # Podemos cambiar los colores de la barra de vida
        if fill <= 26:
            border = pygame.Rect(x, y, bar_lenght, bar_height)
            fill = pygame.Rect(x, y, fill, bar_height)
            pygame.draw.rect(surface, RED, fill)
            pygame.draw.rect(surface, WHITE, border, 2)
        elif fill <= 76:
            border = pygame.Rect(x, y, bar_lenght, bar_height)
            fill = pygame.Rect(x, y, fill, bar_height)
            pygame.draw.rect(surface, YELLOW, fill)
            pygame.draw.rect(surface, WHITE, border, 2)
        else:
            border = pygame.Rect(x, y, bar_lenght, bar_height)
            fill = pygame.Rect(x, y, fill, bar_height)
            pygame.draw.rect(surface, GREEN, fill)
            pygame.draw.rect(surface, WHITE, border, 2)

    def show_go_screen(self):
        screen.blit(bg_img, [0, 0])
        self.draw_text(screen, "Starship Shooter 2023", 65, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        self.draw_text(screen, "Welcome to Deep Space Madness", 27, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.draw_text(screen, "Right Click to pause", 20, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 5/8)
        self.draw_text(screen, "W, A, S, D to move", 20, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 6/8)
        self.draw_text(screen, "Left Click to continue and FIRE", 20, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 7/8)
        pygame.display.flip()
        waiting = True
        while waiting:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
    
    def pause_game(self):
        screen.blit(bg_img, [0, 0])
        self.draw_text(screen, "Starship Shooter 2023", 65, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        self.draw_text(screen, "PAUSE", 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.draw_text(screen, "Left Click to continue", 20, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3/4)
        pygame.display.flip()
        waiting = True
        while waiting:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()

    def display_frame(self, screen):
        screen.blit(bg_img, [0, 0])
        self.all_sprites_set.draw(screen)
        self.draw_life_bar(screen, self.player.life_bar, 5, 5)
        self.draw_text(screen, "SCORE "+ str(self.score), 25, SCREEN_WIDTH // 2 , 10)
        self.draw_text(screen, "MAX SCORE " + str(self.max_score()), 25, SCREEN_WIDTH - 110 , 10)
        pygame.display.flip()

# --- Función Principal del Juego --- #

def main():
    pygame.init()
    # Para reproducir la música se debe hacer fuera del bucle while principal
    # Esto es porque el bucle principal posee un clock a 60 FPS
    pygame.mixer.init()
    pygame.mixer.music.load("assets/sounds/music.ogg")
    pygame.mixer.music.set_volume(0.7)
    pygame.mixer.music.play(-1)

    done = False
    game = Game()
    game.show_go_screen()
    while not done:
        done = game.process_events()
        game.run_logic()
        game.display_frame(screen)
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()