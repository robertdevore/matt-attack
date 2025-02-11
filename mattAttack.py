import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Matt Attack")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Clock for controlling the frame rate
clock = pygame.time.Clock()
FPS = 60

# Mode selection
def select_mode():
    font = pygame.font.Font(None, 48)
    screen.fill(BLACK)
    sfw_text = font.render("Press S for SFW Mode", True, WHITE)
    nsfw_text = font.render("Press N for NSFW Mode", True, WHITE)
    screen.blit(sfw_text, (WIDTH // 2 - sfw_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(nsfw_text, (WIDTH // 2 - nsfw_text.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    return "sfw"
                elif event.key == pygame.K_n:
                    return "nsfw"

# Determine mode and set image path accordingly
mode = select_mode()
image_path = f"images/{mode}/"

# Load images
player_image = pygame.image.load(f"{image_path}player.png")
matt_images = [pygame.image.load(f"{image_path}matt-{i}.png") for i in range(1, 6)]
bullet_image = pygame.image.load(f"{image_path}bullet.png")
background_image = pygame.image.load(f"{image_path}background.jpg")

# Load sounds (these are currently mode-agnostic)
pygame.mixer.init()
background_music = pygame.mixer.Sound("background.wav")
gun_sound = pygame.mixer.Sound("gunshot.wav")
explosion_sound = pygame.mixer.Sound("explosion.wav")
game_over_sound = pygame.mixer.Sound("game-over.wav")

# Play background music on loop
background_music.play(-1)

# Classes for the game
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(player_image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 50)
        self.speed = 5

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        bullets.add(bullet)
        gun_sound.play()

class Matt(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = random.choice(matt_images)
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(2, 5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.y = random.randint(-100, -40)
            self.rect.x = random.randint(0, WIDTH - self.rect.width)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(bullet_image, (10, 20))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = -7

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# Sprite groups
player = Player()
players = pygame.sprite.Group(player)
matts = pygame.sprite.Group()
for _ in range(10):  # Create 10 enemies
    matts.add(Matt())
bullets = pygame.sprite.Group()

# Variables for lives and accumulative score
lives = 3
score = 0

def game_over_screen(final_score):
    font = pygame.font.Font(None, 72)
    screen.fill(BLACK)
    game_over_text = font.render("Game Over!", True, WHITE)
    score_text = font.render(f"Final Score: {final_score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()
    pygame.time.wait(5000)  # Wait for 5 seconds before closing

# Main game loop
running = True
while running:
    screen.blit(background_image, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # Update sprites
    keys = pygame.key.get_pressed()
    player.update(keys)
    matts.update()
    bullets.update()

    # Check collisions between bullets and enemies
    hits = pygame.sprite.groupcollide(matts, bullets, True, True)
    for hit in hits:
        explosion_sound.play()
        score += 10
        matts.add(Matt())

    # Check for collisions between enemies and the player
    if pygame.sprite.spritecollideany(player, matts):
        lives -= 1
        if lives > 0:
            # Reset the player and enemies; clear bullets
            player.rect.center = (WIDTH // 2, HEIGHT - 50)
            bullets.empty()
            matts.empty()
            for _ in range(10):
                matts.add(Matt())
            pygame.time.wait(1000)  # Brief pause before resuming
        else:
            game_over_sound.play()
            game_over_screen(score)
            running = False

    # Draw sprites
    players.draw(screen)
    matts.draw(screen)
    bullets.draw(screen)

    # Display the current score and lives
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 50))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
