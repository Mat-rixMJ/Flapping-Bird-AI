import pygame
import random
import os
import neat
import math
import sys
import pickle


# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.25
FLAP_STRENGTH = -7
INITIAL_PIPE_SPEED = 3
GENERATION = 0

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
GRASS_DARK = (28, 120, 28)
BIRD_YELLOW = (255, 215, 0)
BIRD_ORANGE = (255, 140, 0)
BIRD_WHITE = (255, 255, 240)
PIPE_GREEN = (40, 180, 99)
PIPE_DARK = (35, 150, 80)

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.size = 25
        self.wing_angle = 0
        self.alive = True
        self.fitness = 0

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        # Apply gravity and update position
        self.velocity += GRAVITY
        self.y += self.velocity
        
        # Update wing animation
        self.wing_angle += 0.2
        if self.wing_angle > 2 * math.pi:
            self.wing_angle = 0

        # Keep bird within screen bounds
        if self.y < 0:
            self.y = 0
            self.velocity = 0
        elif self.y > SCREEN_HEIGHT - self.size:
            self.y = SCREEN_HEIGHT - self.size
            self.velocity = 0
            self.alive = False

    def draw(self, screen):
        # Draw main body (gradient)
        for i in range(self.size//2):
            color = (255, 215 + i, i)
            pygame.draw.circle(screen, color, 
                             (self.x - self.size//2, self.y + self.size//2), 
                             self.size//2 - i)

        # Draw tail feathers with detail
        tail_points = [
            (self.x - self.size, self.y + self.size//2),
            (self.x - self.size - 12, self.y + self.size//4),
            (self.x - self.size - 15, self.y + self.size//2),
            (self.x - self.size - 12, self.y + 3*self.size//4)
        ]
        pygame.draw.polygon(screen, BIRD_YELLOW, tail_points)
        for i in range(3):
            start = (self.x - self.size, self.y + self.size//2)
            end = (self.x - self.size - 12, self.y + self.size//3 + i*self.size//3)
            pygame.draw.line(screen, (200, 160, 0), start, end, 2)

        # Draw wings with animation
        wing_offset = math.sin(self.wing_angle) * 5
        # Back wing
        back_wing_points = [
            (self.x - self.size//2 - 5, self.y + self.size//2),
            (self.x - self.size//4 - 5, self.y + wing_offset + 5),
            (self.x - 3*self.size//4 - 5, self.y + self.size//4 + wing_offset + 5)
        ]
        pygame.draw.polygon(screen, (220, 220, 205), back_wing_points)
        # Front wing
        front_wing_points = [
            (self.x - self.size//2, self.y + self.size//2),
            (self.x - self.size//4, self.y + wing_offset),
            (self.x - 3*self.size//4, self.y + self.size//4 + wing_offset)
        ]
        pygame.draw.polygon(screen, BIRD_WHITE, front_wing_points)
        
        # Draw beak with detail
        beak_points = [
            (self.x + 2, self.y + self.size//2),
            (self.x - self.size//4, self.y + self.size//3),
            (self.x - self.size//4, self.y + 2*self.size//3)
        ]
        pygame.draw.polygon(screen, BIRD_ORANGE, beak_points)
        pygame.draw.line(screen, (200, 100, 0), 
                        (self.x - self.size//4, self.y + self.size//2),
                        (self.x + 2, self.y + self.size//2), 2)
        
        # Draw eye with detail
        pygame.draw.circle(screen, WHITE, (self.x - self.size//3, self.y + self.size//2), 4)
        pygame.draw.circle(screen, BLACK, (self.x - self.size//3, self.y + self.size//2), 2)

class Pipe:
    def __init__(self, difficulty_level=0):
        self.gap_y = random.randint(200, SCREEN_HEIGHT - 200)
        self.x = SCREEN_WIDTH
        self.width = 50
        # Decrease gap size more gradually
        self.gap_size = max(150, 200 - (difficulty_level * 5))  # Changed from 10 to 5, min from 100 to 150
        # Increase speed more gradually
        self.speed = INITIAL_PIPE_SPEED + (difficulty_level * 0.25)  # Changed from 0.5 to 0.25
        self.passed = False

    def update(self):
        self.x -= self.speed

    def draw(self, screen):
        # Draw pipes with texture
        top_height = self.gap_y - self.gap_size // 2
        bottom_start = self.gap_y + self.gap_size // 2
        
        # Draw main pipes
        pygame.draw.rect(screen, PIPE_GREEN, (self.x, 0, self.width, top_height))
        pygame.draw.rect(screen, PIPE_GREEN, (self.x, bottom_start, self.width, SCREEN_HEIGHT - bottom_start))
        
        # Add pipe texture (vertical stripes)
        for x in range(int(self.x), int(self.x + self.width), 10):
            pygame.draw.line(screen, PIPE_DARK, (x, 0), (x, top_height), 2)
            pygame.draw.line(screen, PIPE_DARK, (x, bottom_start), (x, SCREEN_HEIGHT), 2)

    def collides_with(self, bird):
        bird_rect = pygame.Rect(bird.x - bird.size, bird.y, bird.size, bird.size)
        top_pipe = pygame.Rect(self.x, 0, self.width, self.gap_y - self.gap_size // 2)
        bottom_pipe = pygame.Rect(self.x, self.gap_y + self.gap_size // 2, 
                                self.width, SCREEN_HEIGHT - (self.gap_y + self.gap_size // 2))
        return bird_rect.colliderect(top_pipe) or bird_rect.colliderect(bottom_pipe)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flapping Bird AI")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset()

    def reset(self):
        self.pipes = [Pipe(0)]  # Start with difficulty level 0
        self.score = 0
        self.frame_iteration = 0
        self.difficulty_level = 0

    def update_fitness(self, birds):
        # Update fitness for each bird based on survival time and pipe passing
        for bird in birds:
            if bird.alive:
                bird.fitness += 0.1  # Reward for surviving
                # Extra reward for getting closer to pipe center
                if self.pipes:
                    pipe = self.pipes[0]
                    if pipe.x < bird.x and not pipe.passed:
                        vertical_distance = abs(bird.y - pipe.gap_y)
                        bird.fitness += (100 - vertical_distance) / 100  # More reward for staying centered

    def draw(self, birds, generation):
        # Draw background
        self.screen.fill(SKY_BLUE)
        
        # Draw ground
        pygame.draw.rect(self.screen, GRASS_GREEN, (0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20))
        for i in range(0, SCREEN_WIDTH, 30):
            points = [(i, SCREEN_HEIGHT - 20), (i + 15, SCREEN_HEIGHT - 30), (i + 30, SCREEN_HEIGHT - 20)]
            pygame.draw.polygon(self.screen, GRASS_DARK, points)
        
        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(self.screen)
        
        # Draw birds
        for bird in birds:
            if bird.alive:
                bird.draw(self.screen)
        
        # Draw stats
        score_text = self.font.render(f'Score: {self.score}', True, BLACK)
        gen_text = self.font.render(f'Generation: {generation}', True, BLACK)
        alive_text = self.font.render(f'Alive: {sum(1 for bird in birds if bird.alive)}', True, BLACK)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(gen_text, (10, 50))
        self.screen.blit(alive_text, (10, 90))
        
        pygame.display.flip()

def save_checkpoint(genome, score, generation):
    """Save a checkpoint of the model when reaching significant scores"""
    filename = f"checkpoint_gen{generation}_score{score}.pkl"
    with open(filename, "wb") as f:
        pickle.dump(genome, f)
    print(f"\nCheckpoint saved! Generation: {generation}, Score: {score}")

def eval_genomes(genomes, config):
    global GENERATION
    GENERATION += 1
    
    # Create neural networks and birds
    nets = []
    birds = []
    ge = []
    
    # Track if we've saved a checkpoint for score 100
    checkpoint_saved = False
    
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2))
        genome.fitness = 0
        ge.append(genome)

    # Create game instance
    game = Game()
    
    # Game loop
    running = True
    while running and any(bird.alive for bird in birds):
        game.frame_iteration += 1
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # Get pipe index for neural network input
        pipe_idx = 0
        if len(game.pipes) > 1 and game.pipes[0].x < birds[0].x:
            pipe_idx = 1
        
        # Update each bird
        for x, bird in enumerate(birds):
            if bird.alive:
                bird.update()
                ge[x].fitness += 0.1
                
                # Neural network inputs
                output = nets[x].activate((
                    bird.y,
                    abs(bird.y - game.pipes[pipe_idx].gap_y),
                    abs(bird.x - game.pipes[pipe_idx].x)
                ))
                
                if output[0] > 0.5:
                    bird.flap()
        
        # Update pipes
        rem = []
        add_pipe = False
        for pipe in game.pipes:
            pipe.update()
            
            # Check collisions
            for x, bird in enumerate(birds):
                if bird.alive and pipe.collides_with(bird):
                    bird.alive = False
                
                if bird.alive and not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            
            if pipe.x + pipe.width < 0:
                rem.append(pipe)
        
        if add_pipe:
            game.score += 1
            
            # Increase difficulty every 15 points, with a maximum level
            if game.score % 15 == 0:
                # Cap difficulty at level 5 to prevent it from becoming too hard
                if game.difficulty_level < 5:
                    game.difficulty_level += 1
                    print(f"\nDifficulty increased! Level: {game.difficulty_level}")
                    print(f"Gap size: {200 - (game.difficulty_level * 5)}, Speed: {INITIAL_PIPE_SPEED + (game.difficulty_level * 0.25)}")
            
            for genome in ge:
                genome.fitness += 5
            
            # Create new pipe with current difficulty level
            game.pipes.append(Pipe(game.difficulty_level))
        
        for pipe in rem:
            game.pipes.remove(pipe)
        
        # Update fitness based on performance
        game.update_fitness(birds)
        
        # Draw game state
        game.draw(birds, GENERATION)
        game.clock.tick(60)
        
        # Save checkpoint when score reaches 100
        if game.score >= 100 and not checkpoint_saved:
            # Find the best performing genome
            best_genome = None
            best_fitness = float('-inf')
            for x, genome in enumerate(ge):
                if genome.fitness > best_fitness:
                    best_fitness = genome.fitness
                    best_genome = genome
            
            if best_genome:
                save_checkpoint(best_genome, game.score, GENERATION)
                checkpoint_saved = True

def run_neat(config_path):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        config_path)
    
    pop = neat.Population(config)
    
    # Add reporters for stats
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    
    # Run evolution
    winner = pop.run(eval_genomes, 50)
    print('\nBest genome:\n{!s}'.format(winner))
    with open("best_genome.pkl", "wb") as f:
        pickle.dump(winner, f)


def load_best_genome(config):
    """Load the best genome from file"""
    try:
        with open("best_genome.pkl", "rb") as f:
            genome = pickle.load(f)
        return genome
    except FileNotFoundError:
        print("No saved model found. Please train first.")
        return None

def run_winner(config, genome):
    """Run the game with the best genome"""
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    bird = Bird(SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2)
    game = Game()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        pipe_idx = 0
        if len(game.pipes) > 1 and game.pipes[0].x < bird.x:
            pipe_idx = 1
            
        output = net.activate((
            bird.y,
            abs(bird.y - game.pipes[pipe_idx].gap_y),
            abs(bird.x - game.pipes[pipe_idx].x)
        ))
        
        if output[0] > 0.5:
            bird.flap()
            
        # Update game state
        bird.update()
        game.update_fitness([bird])
        game.draw([bird], "Best Model")
        game.clock.tick(60)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        config_path)
    
    if len(sys.argv) > 1 and sys.argv[1] == "play":
        # Play mode - load and run best genome
        genome = load_best_genome(config)
        if genome:
            run_winner(config, genome)
    else:
        # Training mode
        run_neat(config_path)
