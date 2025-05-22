import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.25
FLAP_STRENGTH = -7
INITIAL_PIPE_SPEED = 3
MIN_PIPE_SPEED = 3
MAX_PIPE_SPEED = 7
INITIAL_PIPE_SPAWN_TIME = 1500  # milliseconds
MIN_PIPE_SPAWN_TIME = 800  # milliseconds
INITIAL_PIPE_GAP = 200
MIN_PIPE_GAP = 120
DIFFICULTY_INCREASE_SCORE = 10  # Increase difficulty every 10 points

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
GRASS_DARK = (28, 120, 28)
BIRD_YELLOW = (255, 215, 0)
BIRD_ORANGE = (255, 140, 0)  # For beak
BIRD_WHITE = (255, 255, 240)  # For wing
PIPE_GREEN = (40, 180, 99)
PIPE_DARK = (35, 150, 80)
CLOUD_WHITE = (240, 240, 240)
SUN_YELLOW = (255, 255, 0)

# Game elements
CLOUD_POSITIONS = [(50, 100), (200, 150), (350, 80)]  # x, y positions for clouds

class Bird:
    def __init__(self):
        self.x = SCREEN_WIDTH // 3
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.size = 25  # Increased size
        self.wing_angle = 0  # For smooth wing animation

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        # Keep bird within screen bounds
        if self.y < 0:
            self.y = 0
            self.velocity = 0
        elif self.y > SCREEN_HEIGHT - self.size:
            self.y = SCREEN_HEIGHT - self.size
            self.velocity = 0
        
        # Update wing animation
        self.wing_angle += 0.2
        if self.wing_angle > 2 * math.pi:
            self.wing_angle = 0

    def draw(self, screen):
        # Draw main body (gradient from yellow to lighter yellow)
        for i in range(self.size//2):
            color = (255, 215 + i, i)  # Gradient from BIRD_YELLOW to lighter
            pygame.draw.circle(screen, color, 
                             (self.x - self.size//2, self.y + self.size//2), 
                             self.size//2 - i)

        # Draw detailed tail feathers
        tail_points = [
            (self.x - self.size, self.y + self.size//2),  # Center
            (self.x - self.size - 12, self.y + self.size//4),  # Top
            (self.x - self.size - 15, self.y + self.size//2),  # Middle
            (self.x - self.size - 12, self.y + 3*self.size//4)  # Bottom
        ]
        pygame.draw.polygon(screen, BIRD_YELLOW, tail_points)
        # Add tail detail lines
        for i in range(3):
            start = (self.x - self.size, self.y + self.size//2)
            end = (self.x - self.size - 12, self.y + self.size//3 + i*self.size//3)
            pygame.draw.line(screen, (200, 160, 0), start, end, 2)

        # Draw wings with smooth animation
        wing_offset = math.sin(self.wing_angle) * 5
        # Back wing (slightly darker)
        back_wing_points = [
            (self.x - self.size//2 - 5, self.y + self.size//2),  # Center
            (self.x - self.size//4 - 5, self.y + wing_offset + 5),  # Top
            (self.x - 3*self.size//4 - 5, self.y + self.size//4 + wing_offset + 5)  # Back
        ]
        pygame.draw.polygon(screen, (220, 220, 205), back_wing_points)
        # Front wing
        front_wing_points = [
            (self.x - self.size//2, self.y + self.size//2),  # Center
            (self.x - self.size//4, self.y + wing_offset),  # Top
            (self.x - 3*self.size//4, self.y + self.size//4 + wing_offset)  # Back
        ]
        pygame.draw.polygon(screen, BIRD_WHITE, front_wing_points)
        
        # Draw beak with gradient
        beak_points = [
            (self.x + 2, self.y + self.size//2),  # Tip
            (self.x - self.size//4, self.y + self.size//3),  # Top
            (self.x - self.size//4, self.y + 2*self.size//3)  # Bottom
        ]
        pygame.draw.polygon(screen, BIRD_ORANGE, beak_points)
        # Add beak detail
        pygame.draw.line(screen, (200, 100, 0), 
                        (self.x - self.size//4, self.y + self.size//2),
                        (self.x + 2, self.y + self.size//2), 2)
        
        # Add eye with detail
        pygame.draw.circle(screen, WHITE, (self.x - self.size//3, self.y + self.size//2), 4)
        pygame.draw.circle(screen, BLACK, (self.x - self.size//3, self.y + self.size//2), 2)

class Pipe:
    def __init__(self, speed, gap_size):
        self.gap_y = random.randint(200, SCREEN_HEIGHT - 200)
        self.x = SCREEN_WIDTH
        self.width = 50
        self.scored = False
        self.speed = speed
        self.gap_size = gap_size

    def update(self):
        self.x -= self.speed

    def draw(self, screen):
        # Draw top pipe with rounded corners at bottom
        top_height = self.gap_y - self.gap_size // 2
        pygame.draw.rect(screen, PIPE_GREEN, (self.x, 0, self.width, top_height))
        pygame.draw.rect(screen, PIPE_GREEN, (self.x - 5, top_height - 20, self.width + 10, 20))
        
        # Draw bottom pipe with rounded corners at top
        bottom_start = self.gap_y + self.gap_size // 2
        bottom_height = SCREEN_HEIGHT - bottom_start
        pygame.draw.rect(screen, PIPE_GREEN, (self.x, bottom_start, self.width, bottom_height))
        pygame.draw.rect(screen, PIPE_GREEN, (self.x - 5, bottom_start, self.width + 10, 20))

    def collides_with(self, bird):
        bird_rect = pygame.Rect(bird.x - bird.size, bird.y, bird.size, bird.size)
        top_pipe = pygame.Rect(self.x, 0, self.width, self.gap_y - self.gap_size // 2)
        bottom_pipe = pygame.Rect(self.x, self.gap_y + self.gap_size // 2, 
                                self.width, SCREEN_HEIGHT - (self.gap_y + self.gap_size // 2))
        return bird_rect.colliderect(top_pipe) or bird_rect.colliderect(bottom_pipe)

class Cloud:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0.5

    def update(self):
        self.x -= self.speed
        if self.x < -50:
            self.x = SCREEN_WIDTH + 50

    def draw(self, screen):
        # Draw multiple circles for fluffy cloud appearance
        pygame.draw.circle(screen, CLOUD_WHITE, (int(self.x), self.y), 20)
        pygame.draw.circle(screen, CLOUD_WHITE, (int(self.x - 15), self.y + 10), 15)
        pygame.draw.circle(screen, CLOUD_WHITE, (int(self.x + 15), self.y + 10), 15)

class ScorePopup:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alpha = 255
        self.lifetime = 30  # frames

    def update(self):
        self.y -= 2
        self.alpha -= 255 / self.lifetime
        self.lifetime -= 1

    def draw(self, screen):
        if self.lifetime > 0:
            font = pygame.font.Font(None, 24)
            alpha_surface = pygame.Surface((30, 20), pygame.SRCALPHA)
            text = font.render("+1", True, BLACK)
            alpha_surface.fill((255, 255, 255, 0))
            alpha_surface.blit(text, (0, 0))
            alpha_surface.set_alpha(int(self.alpha))
            screen.blit(alpha_surface, (self.x, self.y))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flapping Bird")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.pipe_speed = INITIAL_PIPE_SPEED
        self.pipe_spawn_time = INITIAL_PIPE_SPAWN_TIME
        self.pipe_gap = INITIAL_PIPE_GAP
        self.clouds = [Cloud(x, y) for x, y in CLOUD_POSITIONS]
        self.score_popups = []
        self.reset_game()

    def reset_game(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.last_pipe = pygame.time.get_ticks()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.game_over:
                        self.reset_game()
                    else:
                        self.bird.flap()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over:
                    self.reset_game()
                else:
                    self.bird.flap()
        return True

    def update(self):
        if not self.game_over:
            self.bird.update()

            # Update clouds
            for cloud in self.clouds:
                cloud.update()

            # Update score popups
            for popup in self.score_popups[:]:
                popup.update()
                if popup.lifetime <= 0:
                    self.score_popups.remove(popup)

            # Update difficulty based on score
            difficulty_level = self.score // DIFFICULTY_INCREASE_SCORE
            self.pipe_speed = min(MAX_PIPE_SPEED, INITIAL_PIPE_SPEED + difficulty_level * 0.5)
            self.pipe_spawn_time = max(MIN_PIPE_SPAWN_TIME, INITIAL_PIPE_SPAWN_TIME - difficulty_level * 100)
            self.pipe_gap = max(MIN_PIPE_GAP, INITIAL_PIPE_GAP - difficulty_level * 10)

            # Spawn new pipes
            now = pygame.time.get_ticks()
            if now - self.last_pipe > self.pipe_spawn_time:
                self.pipes.append(Pipe(self.pipe_speed, self.pipe_gap))
                self.last_pipe = now

            # Update pipes and check collisions
            for pipe in self.pipes[:]:
                pipe.update()
                if pipe.x + pipe.width < 0:
                    self.pipes.remove(pipe)
                if pipe.collides_with(self.bird):
                    self.game_over = True
                # Score when passing pipe
                if not pipe.scored and pipe.x < self.bird.x:
                    self.score += 1
                    pipe.scored = True
                    # Add score popup
                    self.score_popups.append(ScorePopup(self.bird.x, self.bird.y - 20))

    def draw(self):
        # Fill background with sky color
        self.screen.fill(SKY_BLUE)
        
        # Draw sun
        pygame.draw.circle(self.screen, SUN_YELLOW, (50, 50), 30)
        
        # Draw clouds
        for cloud in self.clouds:
            cloud.draw(self.screen)
        
        # Draw ground with texture
        pygame.draw.rect(self.screen, GRASS_GREEN, (0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20))
        # Add grass details
        for i in range(0, SCREEN_WIDTH, 30):
            points = [(i, SCREEN_HEIGHT - 20), (i + 15, SCREEN_HEIGHT - 30), (i + 30, SCREEN_HEIGHT - 20)]
            pygame.draw.polygon(self.screen, GRASS_DARK, points)
        
        # Draw pipes with texture
        for pipe in self.pipes:
            pipe.draw(self.screen)
            # Add pipe texture (vertical stripes)
            for x in range(int(pipe.x), int(pipe.x + pipe.width), 10):
                pygame.draw.line(self.screen, PIPE_DARK, 
                               (x, 0), 
                               (x, pipe.gap_y - pipe.gap_size // 2), 2)
                pygame.draw.line(self.screen, PIPE_DARK,
                               (x, pipe.gap_y + pipe.gap_size // 2),
                               (x, SCREEN_HEIGHT), 2)
        
        # Draw bird
        self.bird.draw(self.screen)
        
        # Draw score and score popups
        score_text = self.font.render(f'Score: {self.score}', True, BLACK)
        self.screen.blit(score_text, (10, 10))
        for popup in self.score_popups:
            popup.draw(self.screen)
        
        if self.game_over:
            game_over_text = self.font.render('Game Over! Click to restart', True, BLACK)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(game_over_text, text_rect)
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()
