from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# Window size
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 700

# Game state
game_state = ""  # Possible states: "start", "instructions", "playing"

# Reposition buttons at the top-middle side by side
restart_button = {"x1": WINDOW_WIDTH // 2 - 150, "y1": WINDOW_HEIGHT - 50, "x2": WINDOW_WIDTH // 2 - 110,
                  "y2": WINDOW_HEIGHT - 30}  # Restart button
play_pause_button = {"x1": WINDOW_WIDTH // 2 - 50, "y1": WINDOW_HEIGHT - 50, "x2": WINDOW_WIDTH // 2 + 50,
                     "y2": WINDOW_HEIGHT - 30}  # Play/Pause button
game_over_button = {"x1": WINDOW_WIDTH // 2 + 110, "y1": WINDOW_HEIGHT - 50, "x2": WINDOW_WIDTH // 2 + 150,
                    "y2": WINDOW_HEIGHT - 30}  # Exit button

game_paused = False


def draw_start_screen():
    draw_text(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2, "Press 'S' to Start")
    draw_text(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 50, "Press 'B' for Instructions")


def draw_instructions():
    instructions = [
        "Tank 1 Controls (Yellow):",
        "W/S - Move Forward/Backward",
        "A/D - Rotate",
        "SPACE - Shoot",
        "",
        "Tank 2 Controls (Green):",
        "I/K - Move Forward/Backward",
        "J/L - Rotate",
        "/ - Shoot",
        "",
        "Press 'S' to Start"
    ]

    y_pos = WINDOW_HEIGHT // 2 + 150
    for line in instructions:
        draw_text(WINDOW_WIDTH // 2 - 100, y_pos, line)
        y_pos -= 30


def draw_buttons():
    # Draw Restart button (Left arrow)
    glColor3f(0, 1, 0)  # Set the color to green
    midpoint_line(restart_button["x1"] + 10, restart_button["y1"] + 20, restart_button["x1"] + 40,
                  restart_button["y1"] + 20)  # Horizontal line
    midpoint_line(restart_button["x1"] + 10, restart_button["y1"] + 20, restart_button["x1"] + 25,
                  restart_button["y1"] + 30)  # Left diagonal
    midpoint_line(restart_button["x1"] + 10, restart_button["y1"] + 20, restart_button["x1"] + 25,
                  restart_button["y1"] + 10)  # Right diagonal

    # Draw Play/Pause button (Amber || symbol)
    glColor3f(1, 0.85, 0)  # Amber color for play/pause
    if not game_paused:
        midpoint_line(play_pause_button["x1"] + 15, play_pause_button["y1"], play_pause_button["x1"] + 15,
                      play_pause_button["y2"] - 5)
        midpoint_line(play_pause_button["x1"] + 35, play_pause_button["y1"], play_pause_button["x1"] + 35,
                      play_pause_button["y2"] - 5)
    else:
        midpoint_line(play_pause_button["x1"] + 15, play_pause_button["y1"], play_pause_button["x1"] + 15,
                      play_pause_button["y2"] - 5)
        midpoint_line(play_pause_button["x1"] + 15, restart_button["y1"] + 14, play_pause_button["x1"] + 30,
                      restart_button["y1"] + 10)
        midpoint_line(play_pause_button["x1"] + 15, restart_button["y1"], play_pause_button["x1"] + 30,
                      restart_button["y1"] + 10)

    # Draw Exit button (Red Cross)
    glColor3f(1, 0, 0)  # Red color for exit cross
    midpoint_line(game_over_button["x1"] + 5, game_over_button["y1"] + 5, game_over_button["x2"] - 5,
                  game_over_button["y2"] - 5)
    midpoint_line(game_over_button["x2"] - 5, game_over_button["y1"] + 5, game_over_button["x1"] + 5,
                  game_over_button["y2"] - 5)


def mouse_func(button, state, x, y):
    global game_paused
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Adjust y-coordinate to match OpenGL's coordinate system (invert y-axis)
        y = WINDOW_HEIGHT - y  # In OpenGL, (0, 0) is at the bottom-left corner, so we need to invert y

        # Check if the play/pause button was clicked
        if play_pause_button["x1"] <= x <= play_pause_button["x2"] and play_pause_button["y1"] <= y <= \
                play_pause_button["y2"]:
            game_paused = not game_paused  # Toggle the paused state
            if game_paused:
                print("Game paused.")
            else:
                print("Game resumed.")

        # Check if the restart button was clicked (only if the game is not paused)
        if restart_button["x1"] <= x <= restart_button["x2"] and restart_button["y1"] <= y <= restart_button["y2"]:
            print("Starting over...")
            restart_game()

        # Check if the game over (exit) button was clicked
        if game_over_button["x1"] <= x <= game_over_button["x2"] and game_over_button["y1"] <= y <= game_over_button[
            "y2"]:
            print("Goodbye")
            print(f"Final Score: Tank 1 - {tank1['lives']}, Tank 2 - {tank2['lives']}")
            glutLeaveMainLoop()  # Exit the game

        glutPostRedisplay()  # Request a redraw after an action


# Tank and bullet positions, directions, and game states
tank1 = {"x": 100, "y": 100, "angle": 0, "size": 20, "lives": 10}
tank2 = {"x": 1300, "y": 600, "angle": 180, "size": 20, "lives": 10}

bullets = []

# Control flags for shooting
tank1_can_shoot = True
tank2_can_shoot = True

# Game state
game_over = False
game_tied = False


def draw_text(x, y, text):
    glColor3f(1.0, 1.0, 1.0)  # White color for text
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))


def draw_tank(tank, color):
    glColor3f(*color)  # Set tank color
    midpoint_circle(int(tank["x"]), int(tank["y"]), int(tank["size"]))

    # Draw the cannon direction using midpoint line algorithm
    cannon_length = 30
    cannon_x = tank["x"] + cannon_length * math.cos(math.radians(tank["angle"]))
    cannon_y = tank["y"] + cannon_length * math.sin(math.radians(tank["angle"]))
    midpoint_line(int(tank["x"]), int(tank["y"]), int(cannon_x), int(cannon_y))


def move_tank(tank, direction):
    if game_paused == False:
        speed = 25
        new_x = tank["x"] + direction * speed * math.cos(math.radians(tank["angle"]))
        new_y = tank["y"] + direction * speed * math.sin(math.radians(tank["angle"]))

        # Check boundaries and restrict the tank's movement within the window
        if 0 <= new_x - tank["size"] <= WINDOW_WIDTH and 0 <= new_y - tank["size"] <= WINDOW_HEIGHT:
            tank["x"] = new_x
            tank["y"] = new_y


def rotate_tank(tank, angle_change):
    if game_paused == False:
        tank["angle"] += angle_change


def shoot_bullet(tank, shooter_id):
    if game_paused == False:
        bullet_speed = 10
        bullet_dx = bullet_speed * math.cos(math.radians(tank["angle"]))
        bullet_dy = bullet_speed * math.sin(math.radians(tank["angle"]))

        bullet_color = (1.0, 1.0, 0.0) if shooter_id == "tank1" else (
        0.0, 1.0, 0.0)  # Yellow for tank1, Green for tank2

        bullets.append({
            "x": tank["x"],
            "y": tank["y"],
            "dx": bullet_dx,
            "dy": bullet_dy,
            "shooter": shooter_id,
            "color": bullet_color
        })


def draw_bullet(bullet):
    glColor3f(*bullet["color"])
    midpoint_circle(int(bullet["x"]), int(bullet["y"]), 5)


def update_bullets():
    global bullets, tank1, tank2, game_over, game_tied

    if game_over or game_tied or game_paused:
        return

    new_bullets = []
    for bullet in bullets:
        bullet["x"] += bullet["dx"]
        bullet["y"] += bullet["dy"]

        bullet_hit = False

        # Check collision with obstacles
        for obstacle in obstacles:
            distance = math.sqrt((bullet["x"] - obstacle["x"]) ** 2 + (bullet["y"] - obstacle["y"]) ** 2)
            if distance < obstacle["size"]:
                bullet_hit = True
                break

        # Check tank collisions only if bullet hasn't hit an obstacle
        if not bullet_hit:
            if bullet["shooter"] != "tank1" and (bullet["x"] - tank1["x"]) ** 2 + (bullet["y"] - tank1["y"]) ** 2 <= (
                    tank1["size"] ** 2):
                tank1["lives"] = max(0, tank1["lives"] - 1)
                if tank1["lives"] == 0:
                    game_over = True
                bullet_hit = True
            elif bullet["shooter"] != "tank2" and (bullet["x"] - tank2["x"]) ** 2 + (bullet["y"] - tank2["y"]) ** 2 <= (
                    tank2["size"] ** 2):
                tank2["lives"] = max(0, tank2["lives"] - 1)
                if tank2["lives"] == 0:
                    game_over = True
                bullet_hit = True

        if not bullet_hit and 0 <= bullet["x"] <= WINDOW_WIDTH and 0 <= bullet["y"] <= WINDOW_HEIGHT:
            new_bullets.append(bullet)

    bullets = new_bullets

    # Check for tank collision (tie)
    distance = math.sqrt((tank1["x"] - tank2["x"]) ** 2 + (tank1["y"] - tank2["y"]) ** 2)
    if distance <= (tank1["size"] + tank2["size"]):
        game_tied = True


hearts = []
heart_spawn_time = 0
HEART_DURATION = 10  # seconds
HEART_SIZE = 15


def spawn_heart():
    if game_paused == False:
        heart = {
            "x": random.randint(100, WINDOW_WIDTH - 100),
            "y": random.randint(100, WINDOW_HEIGHT - 100),
            "size": HEART_SIZE,
            "active": True
        }
        hearts.append(heart)


def draw_heart(heart):
    if not heart["active"]:
        return

    glColor3f(1.0, 0.0, 0.0)  # Red color for hearts
    midpoint_circle(int(heart["x"]), int(heart["y"] - 5), int(heart["size"]))
    radius = heart["size"] - 5
    midpoint_circle(int(heart["x"] - radius), int(heart["y"] + radius), int(radius))
    midpoint_circle(int(heart["x"] + radius), int(heart["y"] + radius), int(radius))


def update_hearts():
    if game_over == False and game_tied == False and game_paused == False:
        global hearts, heart_spawn_time
        current_time = glutGet(GLUT_ELAPSED_TIME) / 1000

        if current_time - heart_spawn_time >= HEART_DURATION:
            hearts = []
            spawn_heart()
            heart_spawn_time = current_time

        for heart in hearts:
            if not heart["active"]:
                continue

            distance1 = math.sqrt((tank1["x"] - heart["x"]) ** 2 + (tank1["y"] - heart["y"]) ** 2)
            if distance1 < (tank1["size"] + heart["size"]):
                tank1["lives"] = min(tank1["lives"] + 5, 99)
                heart["active"] = False

            distance2 = math.sqrt((tank2["x"] - heart["x"]) ** 2 + (tank2["y"] - heart["y"]) ** 2)
            if distance2 < (tank2["size"] + heart["size"]):
                tank2["lives"] = min(tank2["lives"] + 5, 99)
                heart["active"] = False


def draw_hexagon(cx, cy, size, angle):
    points = []
    for i in range(6):
        theta = math.radians(60 * i + angle)
        x = cx + size * math.cos(theta)
        y = cy + size * math.sin(theta)
        points.append((int(x), int(y)))

    for i in range(6):
        next_i = (i + 1) % 6
        midpoint_line(points[i][0], points[i][1], points[next_i][0], points[next_i][1])


obstacles = []
NUM_OBSTACLES = 5


def init_obstacles():
    global obstacles
    obstacles = []
    for _ in range(NUM_OBSTACLES):
        obstacle = {
            "x": random.randint(200, WINDOW_WIDTH - 200),
            "y": random.randint(200, WINDOW_HEIGHT - 200),
            "size": random.randint(30, 50),
            "dx": random.choice([-0.5, -0.3, 0.3, 0.5]),
            "dy": random.choice([-0.5, -0.3, 0.3, 0.5]),
            "angle": 0,
            "rotation_speed": random.choice([-0.5, 0.5])
        }
        obstacles.append(obstacle)


def update_obstacles():
    global obstacles, tank1, tank2

    if game_over or game_tied or game_paused:  # Don't update if game is over
        return

    for obstacle in obstacles:
        # Update position
        obstacle["x"] += obstacle["dx"]
        obstacle["y"] += obstacle["dy"]
        obstacle["angle"] += obstacle["rotation_speed"]

        # Bounce off walls
        if obstacle["x"] - obstacle["size"] <= 0 or obstacle["x"] + obstacle["size"] >= WINDOW_WIDTH:
            obstacle["dx"] *= -1
        if obstacle["y"] - obstacle["size"] <= 0 or obstacle["y"] + obstacle["size"] >= WINDOW_HEIGHT:
            obstacle["dy"] *= -1

        # Check collision with tanks
        def check_tank_collision(tank):
            distance = math.sqrt((tank["x"] - obstacle["x"]) ** 2 + (tank["y"] - obstacle["y"]) ** 2)
            if distance < (tank["size"] + obstacle["size"]):
                # Prevent lives from going below 0
                tank["lives"] = max(0, tank["lives"] - 1)

                if tank["lives"] == 0:  # Check if this hit caused game over
                    global game_over
                    game_over = True
                    return

                # Only bounce if game isn't over
                angle = math.atan2(tank["y"] - obstacle["y"], tank["x"] - obstacle["x"])
                pushback = 30
                tank["x"] += math.cos(angle) * pushback
                tank["y"] += math.sin(angle) * pushback
                tank["x"] = max(tank["size"], min(WINDOW_WIDTH - tank["size"], tank["x"]))
                tank["y"] = max(tank["size"], min(WINDOW_HEIGHT - tank["size"], tank["y"]))

        check_tank_collision(tank1)
        check_tank_collision(tank2)


# Mid-point line algorithm
def midpoint_line(x0, y0, x1, y1):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    glBegin(GL_POINTS)
    while True:
        glVertex2i(int(x0), int(y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    glEnd()

# Mid-point circle algorithm
def midpoint_circle(cx, cy, radius):
    x = radius
    y = 0
    p = 1 - radius

    glBegin(GL_POINTS)
    while x >= y:
        plot_circle_points(cx, cy, x, y)
        y += 1
        if p < 0:
            p = p + 2 * y + 1
        else:
            x -= 1
            p = p + 2 * y - 2 * x + 1
    glEnd()

# Plot the 8 points of a circle
def plot_circle_points(cx, cy, x, y):
    glVertex2i(int(cx + x), int(cy + y))
    glVertex2i(int(cx - x), int(cy + y))
    glVertex2i(int(cx + x), int(cy - y))
    glVertex2i(int(cx - x), int(cy - y))
    glVertex2i(int(cx + y), int(cy + x))
    glVertex2i(int(cx - y), int(cy + x))
    glVertex2i(int(cx + y), int(cy - x))
    glVertex2i(int(cx - y), int(cy - x))

# Set up the OpenGL environment
def iterate():
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, WINDOW_WIDTH, 0.0, WINDOW_HEIGHT, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

# Display function for rendering the game
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()

    if game_state == "":

        draw_instructions()

    if game_state == "start":
        update_bullets()
        update_obstacles()
        update_hearts()  # Add this line

        # Set color for obstacles
        glColor3f(1.0, 0.5, 0.0)  # Orange color
        # Draw obstacles
        for obstacle in obstacles:
            draw_hexagon(obstacle["x"], obstacle["y"], obstacle["size"], obstacle["angle"])

        # Draw hearts
        for heart in hearts:  # Add this section
            draw_heart(heart)

        # Set color back to white for tanks
        glColor3f(1.0, 1.0, 1.0)
        draw_tank(tank1, (1, 1, 0))
        draw_tank(tank2, (0, 1, 0))

        for bullet in bullets:
            draw_bullet(bullet)

        draw_text(50, 650, f'Tank 1 Lives: {tank1["lives"]}')
        draw_text(1200, 650, f'Tank 2 Lives: {tank2["lives"]}')

        if game_over:
            draw_text(600, 350, "Game Over")
            winner = "Tank 2" if tank1["lives"] <= 0 else "Tank 1"
            draw_text(600, 300, f"{winner} Wins! Press 'R' to restart")
        elif game_tied:
            draw_text(600, 350, "Game Tied!Press 'R' to restart")


        glutMouseFunc(mouse_func)
        draw_buttons()
    glutSwapBuffers()


# Key press handling for movement and shooting
def keyPressed(*args):
    global tank1_can_shoot, tank2_can_shoot, game_over, game_tied, game_state

    if game_over or game_tied:
        if args[0] == b'r':  # Restart game when 'r' is pressed
            restart_game()
        return
    if args[0] == b's':
        game_state = "start"
    # Tank 1 controls
    if args[0] == b'w':
        move_tank(tank1, 1)
    elif args[0] == b's':
        move_tank(tank1, -1)
    elif args[0] == b'a':
        rotate_tank(tank1, 5)
    elif args[0] == b'd':
        rotate_tank(tank1, -5)
    elif args[0] == b' ' and tank1_can_shoot:
        shoot_bullet(tank1, "tank1")
        tank1_can_shoot = False  # Disable shooting until key is released

    # Tank 2 controls
    if args[0] == b'i':
        move_tank(tank2, 1)
    elif args[0] == b'k':
        move_tank(tank2, -1)
    elif args[0] == b'j':
        rotate_tank(tank2, 5)
    elif args[0] == b'l':
        rotate_tank(tank2, -5)
    elif args[0] == b'/' and tank2_can_shoot:
        shoot_bullet(tank2, "tank2")
        tank2_can_shoot = False  # Disable shooting until key is released

    glutPostRedisplay()


# Key release handler for shooting
def keyReleased(*args):
    global tank1_can_shoot, tank2_can_shoot

    # Reset the shooting flag when the key is released
    if args[0] == b' ':
        tank1_can_shoot = True
    elif args[0] == b'/':
        tank2_can_shoot = True


# Restart the game
def restart_game():
    global tank1, tank2, bullets, hearts, game_over, game_tied, heart_spawn_time
    tank1 = {"x": 100, "y": 100, "angle": 0, "size": 20, "lives": 10}
    tank2 = {"x": 1300, "y": 600, "angle": 180, "size": 20, "lives": 10}
    bullets = []
    hearts = []
    heart_spawn_time = glutGet(GLUT_ELAPSED_TIME) / 1000  # Initialize spawn timer
    init_obstacles()
    game_over = False
    game_tied = False


# Modified main function
def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Tank Battle Game")
    init_obstacles()  # Initialize obstacles at start
    glutDisplayFunc(showScreen)
    glutIdleFunc(showScreen)
    glutKeyboardFunc(keyPressed)
    glutKeyboardUpFunc(keyReleased)
    glutMainLoop()


if __name__ == "__main__":
    main()
