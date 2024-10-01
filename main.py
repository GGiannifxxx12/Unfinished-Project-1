import pygame
import math

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Pyoom')

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ENEMY_COLOR = (255, 0, 0)  # Color for enemies
WALL_COLOR = (200, 100, 50)  # Base color for walls
FLOOR_COLOR = (150, 75, 0)  # Color for the floor
SKY_COLOR = (135, 206, 235)  # Sky color

# Grid settings
cell_size = 40
grid_width = width // cell_size
grid_height = height // cell_size

# Initialize the grid with tuples (type, height)
grid = [[(0, 0) for _ in range(grid_width)] for _ in range(grid_height)]

# Enemy list (position and velocity)
enemies = [[300, 300]]  # Example starting position

# Player settings
player_pos = [150, 150]  # Start player in the middle of the map
player_angle = 0  # Player's looking angle (in radians)
player_speed = 0.1 # Movement speed
turn_speed = 0.05  # Turn speed (radians per frame)
player_radius = 10  # Collision radius for player
gravity = 0.5  # Gravity effect
jump_height = -10  # Initial jump velocity
is_jumping = False
vertical_velocity = 0
ground_level = 150  # Ground level

# Raycasting settings
num_rays = 120  # Number of rays to cast
max_depth = 300  # Max distance for raycasting

# Function to check if a position is within a wall
def is_collision(x, y):
    col = int(x // cell_size)
    row = int(y // cell_size)
    if 0 <= col < grid_width and 0 <= row < grid_height:
        if grid[row][col][0] == 1:  # Wall
            return True
    return False

# Function to check collision with enemies
def check_enemy_collision(new_x, new_y, radius=10):
    for enemy in enemies:
        dist = math.sqrt((enemy[0] - new_x)**2 + (enemy[1] - new_y)**2)
        if dist < radius * 2:  # If too close to an enemy
            return True
    return False

# Function to handle movement with collision detection
def handle_movement(keys):
    global player_pos, player_angle, is_jumping, vertical_velocity

    new_x, new_y = player_pos[0], player_pos[1]

    # Horizontal movement
    if keys[pygame.K_w]:
        new_x += player_speed * math.cos(player_angle)
        new_y += player_speed * math.sin(player_angle)
    if keys[pygame.K_s]:
        new_x -= player_speed * math.cos(player_angle)
        new_y -= player_speed * math.sin(player_angle)
    if keys[pygame.K_a]:
        player_angle -= turn_speed
    if keys[pygame.K_d]:
        player_angle += turn_speed

    # Check for wall collision
    if not is_collision(new_x, new_y) and not check_enemy_collision(new_x, new_y):
        player_pos[0], player_pos[1] = new_x, new_y

    # Jumping mechanics
    if keys[pygame.K_SPACE] and not is_jumping:
        is_jumping = True
        vertical_velocity = jump_height

    if is_jumping:
        vertical_velocity += gravity  # Apply gravity
        player_pos[1] += vertical_velocity  # Update vertical position
        if player_pos[1] >= ground_level:  # Reset when hitting ground level
            player_pos[1] = ground_level
            is_jumping = False

# Function to move enemies towards the player with collision
def move_enemies():
    for enemy in enemies:
        dx = player_pos[0] - enemy[0]
        dy = player_pos[1] - enemy[1]
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 10:  # Only move if far from player
            angle_to_player = math.atan2(dy, dx)
            new_x = enemy[0] + 1 * math.cos(angle_to_player)  # Move towards the player
            new_y = enemy[1] + 1 * math.sin(angle_to_player)

            if not is_collision(new_x, new_y) and not check_enemy_collision(new_x, new_y, radius=10):
                enemy[0], enemy[1] = new_x, new_y

# Function to draw the grid in editor mode
def draw_grid():
    for row in range(grid_height):
        for col in range(grid_width):
            rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)
            if grid[row][col][0] == 1:  # Wall
                pygame.draw.rect(screen, WALL_COLOR, rect)
            pygame.draw.rect(screen, WHITE, rect, 1)  # Grid lines

    # Draw enemies in editor mode
    for enemy in enemies:
        pygame.draw.circle(screen, ENEMY_COLOR, (int(enemy[0]), int(enemy[1])), 10)

    # Draw player indicator in editor mode
    player_grid_x = int(player_pos[0] // cell_size)
    player_grid_y = int(player_pos[1] // cell_size)
    player_screen_x = player_grid_x * cell_size + cell_size // 2
    player_screen_y = player_grid_y * cell_size + cell_size // 2
    pygame.draw.circle(screen, GREEN, (player_screen_x, player_screen_y), 5)

# Function to toggle walls in the map editor
def toggle_wall(pos):
    col, row = pos[0] // cell_size, pos[1] // cell_size
    if 0 <= col < grid_width and 0 <= row < grid_height:
        current_type, current_height = grid[row][col]
        if current_type == 0:
            grid[row][col] = (1, 0)  # Add wall
        else:
            grid[row][col] = (0, 0)  # Remove wall

# Cast rays for 3D view
def cast_rays():
    start_angle = player_angle - (math.pi / 6)  # Field of view

    # Draw sky and floor before walls and enemies
    screen.fill(SKY_COLOR)  # Sky (top half)
    pygame.draw.rect(screen, FLOOR_COLOR, (0, height // 2, width, height // 2))  # Floor (bottom half)

    for ray in range(num_rays):
        ray_angle = start_angle + ray * (math.pi / 3 / num_rays)
        ray_angle %= 2 * math.pi  # Normalize the angle

        for depth in range(max_depth):
            target_x = player_pos[0] + depth * math.cos(ray_angle)
            target_y = player_pos[1] + depth * math.sin(ray_angle)

            col = int(target_x // cell_size)
            row = int(target_y // cell_size)

            # Check if the ray hits a wall
            if 0 <= col < grid_width and 0 <= row < grid_height:
                if grid[row][col][0] == 1:  # Wall
                    wall_height = (height / (depth + 0.1)) * 5  # Wall height scaling

                    # Calculate shading based on distance
                    shade_factor = max(0, min(255, int(255 - (depth * 0.5))))
                    shaded_color = (shade_factor, shade_factor // 2, 0)  # Darker shade for distance
                    pygame.draw.rect(screen, shaded_color, (ray * (width // num_rays), height // 2 - wall_height // 2, width // num_rays, wall_height))
                    break

# Render enemies in 3D view
def render_enemies():
    for enemy in enemies:
        # Calculate distance and angle to the player
        dist_x = enemy[0] - player_pos[0]
        dist_y = enemy[1] - player_pos[1]
        distance_to_player = math.sqrt(dist_x**2 + dist_y**2)

        # Angle between enemy and player
        angle_to_player = math.atan2(dist_y, dist_x) - player_angle
        if angle_to_player < -math.pi:
            angle_to_player += 2 * math.pi
        if angle_to_player > math.pi:
            angle_to_player -= 2 * math.pi

        # If enemy is within the player's field of view
        if -math.pi / 6 < angle_to_player < math.pi / 6:
            # Scale enemy size based on distance
            enemy_height = (height / distance_to_player) * 40
            enemy_x = width / 2 + angle_to_player * width / (math.pi / 3)
            pygame.draw.rect(screen, ENEMY_COLOR, (enemy_x - enemy_height // 2, height // 2 - enemy_height // 2, enemy_height, enemy_height))

# Main game loop
running = True
in_editor = True  # Start in editor mode

while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and in_editor:
            if event.button == 1:  # Left-click to place/remove walls in editor
                toggle_wall(pygame.mouse.get_pos())
            if event.button == 3:  # Right-click to place enemies
                enemies.append(list(pygame.mouse.get_pos()))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:  # Toggle between editor and game
                in_editor = not in_editor

    if in_editor:
        draw_grid()  # Draw grid and enemies in editor mode
    else:
        keys = pygame.key.get_pressed()
        handle_movement(keys)
        move_enemies()
        cast_rays()
        render_enemies()

    pygame.display.flip()

pygame.quit()



