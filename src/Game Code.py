# Importing modules
import pygame, sys, math, time, random

# Setting colors
black = pygame.color.Color("Black")
white = pygame.color.Color("White")
green = pygame.color.Color("Green")
red = pygame.color.Color("Red")
blue = pygame.color.Color("Blue")
grey = pygame.color.Color("Grey")

# Classes

class Player:
    def __init__(self, screen, radius, color):
        self.screen = screen
        self.radius = radius
        self.color = color
        self.x_init = self.screen.get_width() // 2
        self.y_init = self.screen.get_height() - self.radius * 2
        self.x = self.x_init
        self.y = self.y_init

    def draw(self):
        pygame.draw.circle(self.screen, self.color, (self.x, self.y), self.radius)

    def move(self):
        pygame.mouse.set_visible(False)
        mouse_x = pygame.mouse.get_pos()[0]
        mouse_y = pygame.mouse.get_pos()[1]
        if self.radius * 2 < mouse_x < self.screen.get_width() - self.radius * 2:
            self.x = mouse_x
        if self.radius * 2 < mouse_y < self.screen.get_height() - self.radius * 2:
            self.y = mouse_y

class Ball:
    def __init__(self, screen, radius, color, speed):
        self.screen = screen
        self.radius = radius
        self.color = color
        self.x_init = self.screen.get_width() // 2
        self.y_init = self.screen.get_height() // 4 * 3
        self.x = self.x_init
        self.y = self.y_init
        self.x_speed = 0
        self.y_speed = 0
        self.speed = speed

    def draw(self):
        pygame.draw.circle(self.screen, self.color, (self.x, self.y), self.radius)

    def check_hit_by(self, player):
        self.x += self.x_speed
        self.y += self.y_speed
        player_hitbox = pygame.Rect(player.x - player.radius, player.y - player.radius,
                                    player.radius * 2, player.radius * 2)
        ball_hitbox = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
        if player_hitbox.colliderect(ball_hitbox):
            self.x_speed = (self.x - player.x) / self.speed
            self.y_speed = (self.y - player.y) / self.speed
            return True

    def check_hit_border(self, player):

        # Hitting left or right border
        if self.x < player.radius:
            self.x = player.radius
        if self.x > self.screen.get_width() - player.radius:
            self.x = self.screen.get_width() - player.radius
        if self.x == player.radius or self.x == self.screen.get_width() - player.radius:
            self.x_speed = -1 * self.x_speed
            return True

        # Hitting top or bottom border
        if self.y < player.radius:
            self.y = player.radius
        if self.y > self.screen.get_height() - player.radius:
            self.y = self.screen.get_height() - player.radius
        if self.y == player.radius or self.y == self.screen.get_height() - player.radius:
            self.y_speed = -1 * self.y_speed
            return True

class Goal:
    def __init__(self, screen, position, length, player, ball, color, is_agent):
        self.screen = screen
        self.position = position
        self.length = length
        self.player = player
        self.ball = ball
        self.color = color
        self.is_agent = is_agent

    def draw(self):

        # For bottom or top goals
        if self.position == "bottom":
            goal_mid_y = self.screen.get_height() - self.player.radius // 2
        if self.position == "top":
            goal_mid_y = self.player.radius // 2
        if self.position == "bottom" or self.position == "top":
            goal_left_x = self.screen.get_width() // 2 - self.length // 2
            goal_right_x = self.screen.get_width() // 2 + self.length // 2
            pygame.draw.line(self.screen, self.color,
                             (goal_left_x, goal_mid_y), (goal_right_x, goal_mid_y), self.player.radius)

        # For left or right goals
        if self.position == "left":
            goal_mid_x = self.player.radius // 2
        if self.position == "right":
            goal_mid_x = self.screen.get_width() - self.player.radius // 2
        if self.position == "left" or self.position == "right":
            goal_top_y = self.screen.get_height() // 2 - self.length // 2
            goal_bottom_y = self.screen.get_height() // 2 + self.length // 2
            pygame.draw.line(self.screen, self.color,
                             (goal_mid_x, goal_top_y), (goal_mid_x, goal_bottom_y), self.player.radius)

    def check_goal_in(self):

        # For bottom or top goals
        if self.position == "bottom":
            goal_in_y_top = self.screen.get_height() - self.player.radius - self.ball.radius * 2
            goal_in_y_bottom = self.screen.get_height() - self.player.radius
        if self.position == "top":
            goal_in_y_top = self.player.radius
            goal_in_y_bottom = self.player.radius + self.ball.radius * 2
        if self.position == "bottom" or self.position == "top":
            goal_in_x_left = self.screen.get_width() // 2 - self.length // 2 + self.ball.radius
            goal_in_x_right = self.screen.get_width() // 2 + self.length // 2 - self.ball.radius

        # For left or right goals
        if self.position == "left":
            goal_in_x_left = self.player.radius
            goal_in_x_right = self.player.radius + self.ball.radius * 2
        if self.position == "right":
            goal_in_x_left = self.screen.get_width() - self.player.radius - self.ball.radius * 2
            goal_in_x_right = self.screen.get_width() - self.player.radius
        if self.position == "left" or self.position == "right":
            goal_in_y_top = self.screen.get_height() // 2 - self.length // 2 + self.ball.radius
            goal_in_y_bottom = self.screen.get_height() // 2 + self.length // 2 - self.ball.radius

        # Valid for all goals
        if goal_in_x_left <= self.ball.x <= goal_in_x_right and \
                goal_in_y_top <= self.ball.y <= goal_in_y_bottom:
            if self.is_agent:
                self.color = green
            else:
                self.color = red
            return True

class Agent:
    def __init__(self, screen, player, ball, position, radius, color, speed, defend_speed, goal, bounce_speed):
        self.screen = screen
        self.player = player
        self.ball = ball
        self.position = position
        self.radius = radius
        self.color = color
        self.speed = speed
        self.defend_speed = defend_speed
        self.goal = goal
        self.bounce_speed = bounce_speed

        if self.position == "top":
            self.x_init = self.screen.get_width() // 2
            self.y_init = self.player.radius * 2

        if self.position == "left" or self.position == "right":
            self.y_init = self.screen.get_height() // 2
        if self.position == "left":
            self.x_init = self.player.radius * 2
        if self.position == "right":
            self.x_init = self.screen.get_width() - self.player.radius * 2

        self.x = self.x_init
        self.y = self.y_init

        self.x_speed = 0
        self.y_speed = 0

    def draw(self):
        pygame.draw.circle(self.screen, self.color, (self.x, self.y), self.radius)

    def activate(self):
        target_x = self.ball.x + self.ball.x_speed
        target_y = self.ball.y + self.ball.y_speed
        self.x_speed = target_x - self.x
        self.y_speed = target_y - self.y
        self.x += self.x_speed / self.speed
        self.y += self.y_speed / self.speed

    def defend(self):
        if self.position == "top":
            need_to_defend = self.ball.y <= self.ball.x and self.ball.y <= -1 * self.ball.x + self.screen.get_width()
        if self.position == "left":
            need_to_defend = self.ball.y >= self.ball.x and self.ball.y <= -1 * self.ball.x + self.screen.get_width()
        if self.position == "right":
            need_to_defend = self.ball.y <= self.ball.x and self.ball.y >= -1 * self.ball.x + self.screen.get_width()

        if need_to_defend:
            self.x_speed = self.x_init - self.x
            self.y_speed = self.y_init - self.y
            self.x += self.x_speed / self.defend_speed
            self.y += self.y_speed / self.defend_speed
            return True
        else:
            return False

    def bounce(self, other_agent):
        distance = math.sqrt((self.x - other_agent.x) ** 2 + (self.y - other_agent.y) ** 2)
        if distance <= self.radius * 2 and distance != 0:
            self.x -= self.x_speed / self.bounce_speed
            self.y -= self.y_speed / self.bounce_speed

class Scoreboard:
    def __init__(self, screen):
        self.screen = screen
        self.score = 0
        self.level = 1
        self.font = pygame.font.Font(None, 30)

    def draw(self):
        score_text = "Score: {}".format(self.score)
        score_image = self.font.render(score_text, True, black)
        self.screen.blit(score_image, (self.screen.get_width() - 150, 9))

        level_text = "Level: {}".format(self.level)
        level_image = self.font.render(level_text, True, black)
        self.screen.blit(level_image, (50, 9))

class GUI:
    def __init__(self, screen, menu_size, scoreboard, title_font_size, text_font_size):
        self.screen = screen
        self.menu_size = menu_size
        self.scoreboard = scoreboard
        self.menu_mid_x = self.screen.get_width() // 2
        self.menu_top_y = self.screen.get_height() // 2 - self.menu_size // 2
        self.menu_bottom_y = self.screen.get_height() // 2 + self.menu_size // 2
        self.title_font_size = title_font_size
        self.text_font_size = text_font_size

    def start_menu(self):
        pygame.draw.line(self.screen, black, (self.menu_mid_x, self.menu_top_y),
                         (self.menu_mid_x, self.menu_bottom_y), self.menu_size)

        # Title
        font = pygame.font.Font(None, self.title_font_size)
        title_image = font.render("1 vs 3 Air Hockey", True, white)
        title_x = self.menu_mid_x - title_image.get_width() // 2
        title_y = self.menu_top_y + title_image.get_height() // 2
        self.screen.blit(title_image, (title_x, title_y))

        # Texts
        font = pygame.font.Font(None, self.text_font_size)

        # Keys:
        key_image = font.render("Keys:", True, white)
        key_x = self.menu_mid_x - title_image.get_width() // 2
        key_y = self.menu_top_y + title_image.get_height() * 3
        self.screen.blit(key_image, (key_x, key_y))

        # Start / Pause
        start_image = font.render("Start / Pause [SPACE]", True, white)
        start_x = key_x + key_image.get_width() // 2
        start_y = key_y + key_image.get_height() * 2
        self.screen.blit(start_image, (start_x, start_y))

        # Reposition
        reposition_image = font.render("Reposition [TAB]", True, white)
        reposition_x = key_x + key_image.get_width() // 2
        reposition_y = start_y + key_image.get_height() * 2
        self.screen.blit(reposition_image, (reposition_x, reposition_y))

        # Return to Menu
        pause_image = font.render("Return to menu [ESC]", True, white)
        pause_x = key_x + key_image.get_width() // 2
        pause_y = reposition_y + key_image.get_height() * 2
        self.screen.blit(pause_image, (pause_x, pause_y))

    def pause_menu(self):
        pygame.draw.line(self.screen, black, (self.menu_mid_x, self.menu_top_y),
                         (self.menu_mid_x, self.menu_bottom_y), self.menu_size)

        # Title
        font = pygame.font.Font(None, self.title_font_size)
        title_image = font.render("Paused", True, white)
        title_x = self.menu_mid_x - title_image.get_width() // 2
        title_y = self.menu_top_y + title_image.get_height() // 2
        self.screen.blit(title_image, (title_x, title_y))

        # Texts
        font = pygame.font.Font(None, self.text_font_size)

        # Level and Score
        level_score_text = "Level: {}       Score: {}".format(self.scoreboard.level, self.scoreboard.score)
        level_score_image = font.render(level_score_text, True, white)
        level_score_x = self.menu_mid_x - level_score_image.get_width() // 2
        level_score_y = self.menu_top_y + title_image.get_height() * 2
        self.screen.blit(level_score_image, (level_score_x, level_score_y))

        # Resume
        resume_image = font.render("Resume [ESC]", True, white)
        resume_x = level_score_x
        resume_y = level_score_y + level_score_image.get_height() * 2.5
        self.screen.blit(resume_image, (resume_x, resume_y))

        # Reposition
        reposition_image = font.render("Reposition [TAB]", True, white)
        reposition_x = level_score_x
        reposition_y = resume_y + level_score_image.get_height() * 2
        self.screen.blit(reposition_image, (reposition_x, reposition_y))

        # Reset game
        reset_image = font.render("Restart game [DELETE]", True, white)
        reset_x = level_score_x
        reset_y = reposition_y + level_score_image.get_height() * 2
        self.screen.blit(reset_image, (reset_x, reset_y))

    def level_up(self):
        pygame.draw.line(self.screen, black, (self.menu_mid_x, self.menu_top_y),
                         (self.menu_mid_x, self.menu_bottom_y), self.menu_size)

        # Title
        font = pygame.font.Font(None, self.title_font_size)
        title_text = "Level {} Complete".format(self.scoreboard.level)
        title_image = font.render(title_text, True, white)
        title_x = self.menu_mid_x - title_image.get_width() // 2
        title_y = self.menu_top_y + title_image.get_height() // 2
        self.screen.blit(title_image, (title_x, title_y))

        # Texts
        font = pygame.font.Font(None, self.text_font_size)

        # Score
        score_text = "Score: {}".format(self.scoreboard.score)
        score_image = font.render(score_text, True, white)
        score_x = title_x
        score_y = title_y + title_image.get_height() * 1.5
        self.screen.blit(score_image, (score_x, score_y))

        # Proceed to next level?
        proceed_image = font.render("Proceed to next level?", True, white)
        proceed_x = title_x
        proceed_y = score_y + title_image.get_height() * 1.5
        self.screen.blit(proceed_image, (proceed_x, proceed_y))

        # [ENTER]
        enter_image = font.render("    [ENTER]", True, white)
        enter_x = title_x + proceed_image.get_width() // 2
        enter_y = proceed_y + title_image.get_height()
        self.screen.blit(enter_image, (enter_x, enter_y))

        # Reset game
        reset_image = font.render("Reset game [DELETE]", True, white)
        reset_x = title_x
        reset_y = enter_y + title_image.get_height() * 1.5
        self.screen.blit(reset_image, (reset_x, reset_y))

    def game_over(self):
        pygame.draw.line(self.screen, black, (self.menu_mid_x, self.menu_top_y),
                         (self.menu_mid_x, self.menu_bottom_y), self.menu_size)

        # Title
        font = pygame.font.Font(None, self.title_font_size)
        title_image = font.render("Game Over", True, white)
        title_x = self.menu_mid_x - title_image.get_width() // 2
        title_y = self.menu_top_y + title_image.get_height() // 2
        self.screen.blit(title_image, (title_x, title_y))

        # Texts
        font = pygame.font.Font(None, self.text_font_size)

        # Level and Score
        level_score_text = "Level: {}       Score: {}".format(self.scoreboard.level, self.scoreboard.score)
        level_score_image = font.render(level_score_text, True, white)
        level_score_x = self.menu_mid_x - level_score_image.get_width() // 2
        level_score_y = self.menu_top_y + title_image.get_height() * 2
        self.screen.blit(level_score_image, (level_score_x, level_score_y))

        # Restart
        restart_image = font.render("Restart [DELETE]", True, white)
        restart_x = self.menu_mid_x - restart_image.get_width() // 2
        restart_y = self.screen.get_height() // 2 - restart_image.get_height() // 2
        self.screen.blit(restart_image, (restart_x, restart_y))

    def win_game(self):
        pygame.draw.line(self.screen, black, (self.menu_mid_x, self.menu_top_y),
                         (self.menu_mid_x, self.menu_bottom_y), self.menu_size)

        # Title
        font = pygame.font.Font(None, self.title_font_size)
        title_image = font.render("Congratulations!", True, white)
        title_x = self.menu_mid_x - title_image.get_width() // 2
        title_y = self.menu_top_y + title_image.get_height() // 2
        self.screen.blit(title_image, (title_x, title_y))

        # Texts
        font = pygame.font.Font(None, self.text_font_size)

        # You have won the game!
        victory_image = font.render("You have won the game!", True, white)
        victory_x = self.menu_mid_x - victory_image.get_width() // 2
        victory_y = title_y + title_image.get_height() * 1.5
        self.screen.blit(victory_image, (victory_x, victory_y))

        # Level and Score
        level_score_text = "Level: {}       Score: {}".format(self.scoreboard.level, self.scoreboard.score)
        level_score_image = font.render(level_score_text, True, white)
        level_score_x = self.menu_mid_x - level_score_image.get_width() // 2
        level_score_y = victory_y + title_image.get_height() * 1.5
        self.screen.blit(level_score_image, (level_score_x, level_score_y))

        # Restart
        restart_image = font.render("Restart [DELETE]", True, white)
        restart_x = self.menu_mid_x - restart_image.get_width() // 2
        restart_y = self.screen.get_height() // 2 + restart_image.get_height() * 2
        self.screen.blit(restart_image, (restart_x, restart_y))

# Main Function
def main():
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption("1 vs 3 Air Hockey")
    screen = pygame.display.set_mode((700, 700))

    player1 = Player(screen, 35, green)
    ball1 = Ball(screen, 20, blue, 25)

    goal1 = Goal(screen, "bottom", 100, player1, ball1, grey, False)
    goal2 = Goal(screen, "top", 200, player1, ball1, grey, True)
    goal3 = Goal(screen, "left", 200, player1, ball1, grey, True)
    goal4 = Goal(screen, "right", 200, player1, ball1, grey, True)
    goals = [goal1, goal2, goal3, goal4]

    agent1 = Agent(screen, player1, ball1, "top", 25, red, 100, 20, goal2, 40)
    agent2 = Agent(screen, player1, ball1, "left", 25, red, 100, 20, goal3, 40)
    agent3 = Agent(screen, player1, ball1, "right", 25, red, 100, 20, goal4, 40)
    agents = [agent1, agent2, agent3]

    scoreboard = Scoreboard(screen)
    gui = GUI(screen, 300, scoreboard, 40, 30)

    game_on_if_odd = 0
    pause_menu_if_odd = 0
    level_up_if_odd = 0

    while True:
        clock.tick(60)

        screen.fill(white)  # Fills the screen over everything drawn before, very important
        pygame.draw.line(screen, black, (0, 0), (screen.get_width(), screen.get_height()), 1)
        pygame.draw.line(screen, black, (0, screen.get_height()), (screen.get_width(), 0), 1)
        border_width = screen.get_width() - player1.radius * 2
        pygame.draw.rect(screen, black, (player1.radius, player1.radius, border_width + 1, border_width + 1), 1)

        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if pause_menu_if_odd % 2 == 0:
                if pressed_keys[pygame.K_SPACE]:        # Start
                    game_on_if_odd += 1

            if pressed_keys[pygame.K_ESCAPE]:           # Pause and resume
                game_on_if_odd += 1
                pause_menu_if_odd += 1

            if pressed_keys[pygame.K_DELETE]:           # Reset everything
                game_on_if_odd = 0
                pause_menu_if_odd = 0

                player1.x = player1.x_init
                player1.y = player1.y_init
                ball1.x = ball1.x_init
                ball1.y = ball1.y_init
                ball1.radius = 20
                ball1.speed = 25
                for goal in goals:
                    goal.color = grey
                    if goal.is_agent == True:
                        goal.length = 200
                    else:
                        goal.length = 100
                for agent in agents:
                    agent.x = agent.x_init
                    agent.y = agent.y_init
                    agent.radius = 25
                    agent.speed = 100
                    agent.defend_speed = 20
                    agent.bounce_speed = 40
                scoreboard.score = 0
                scoreboard.level = 1

            if pressed_keys[pygame.K_TAB]:              # Reposition agents
                for agent in agents:
                    agent.x = agent.x_init
                    agent.y = agent.y_init

            if pressed_keys[pygame.K_RETURN]:           # Proceed to next level
                level_up_if_odd += 1

        if game_on_if_odd % 2 == 1:                 # Start game
            player1.move()

            for agent_A in agents:
                if agent_A.defend() == False:
                    agent_A.activate()
                for agent_B in agents:
                    agent_A.bounce(agent_B)
                agent_A.bounce(player1)

            ball1.check_hit_by(player1)
            for agent in agents:
                ball1.check_hit_by(agent)
            ball1.check_hit_border(player1)

            for goal in goals:
                if goal.is_agent == True and goal.color == grey:
                    if goal.check_goal_in() == True:
                        scoreboard.score += 100
                if goal.is_agent == True and goal.color == green:
                    if goal.check_goal_in() == True:
                        scoreboard.score += 10
                goal.check_goal_in()

        player1.draw()
        for agent in agents:
            agent.draw()
        ball1.draw()
        for goal in goals:
            goal.draw()

        scoreboard.draw()

        if game_on_if_odd == 0:
            gui.start_menu()

        if pause_menu_if_odd % 2 == 1:
            gui.pause_menu()

        if goal2.color == green and goal3.color == green and goal4.color == green and scoreboard.level < 3:
            game_on_if_odd = 2
            gui.level_up()
            if level_up_if_odd % 2 == 1:
                # Reset goal color
                for goal in goals:
                    goal.color = grey

                # Increment level by 1
                scoreboard.level += 1

                # Reset all positions
                player1.x = player1.x_init
                player1.y = player1.y_init
                ball1.x = ball1.x_init
                ball1.y = ball1.y_init
                for agent in agents:
                    agent.x = agent.x_init
                    agent.y = agent.y_init

                # Increase difficulty for Level 2
                if scoreboard.level == 2:
                    ball1.radius = 15
                    ball1.speed = 20
                    for agent in agents:
                        agent.radius = 30
                        agent.speed = 50
                        agent.defend_speed = 10
                        agent.bounce_speed = 30
                    for goal in goals:
                        if goal.is_agent == True:
                            goal.length = 150
                        else:
                            goal.length = 150

                # Increase difficulty for Level 3
                if scoreboard.level == 3:
                    ball1.radius = 10
                    ball1.speed = 15
                    for agent in agents:
                        agent.radius = 35
                        agent.speed = 25
                        agent.defend_speed = 5
                        agent.bounce_speed = 20
                    for goal in goals:
                        if goal.is_agent == True:
                            goal.length = 100
                        else:
                            goal.length = 200

                # Reactivate game
                game_on_if_odd += 1

                # Reset level_up_if_odd
                level_up_if_odd = 0

        if goal1.color == red:
            game_on_if_odd = 2
            gui.game_over()

        if goal2.color == green and goal3.color == green and goal4.color == green and scoreboard.level == 3:
            game_on_if_odd = 2
            gui.win_game()

        pygame.display.update()

# Main Function Call
main()



