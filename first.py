import pygame
import random

pygame.init()

screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Aliens vs Cows")
clock = pygame.time.Clock()
dt = 0

screen_width, screen_height = screen.get_size()
bg = pygame.transform.scale(pygame.image.load("bg.png"), (screen_width, screen_height))
bg2 = pygame.transform.scale(pygame.image.load("black.png"), (screen_width, screen_height))
playerSize = 90
cowSize= 80
playerImg = pygame.transform.scale(pygame.image.load('ufo.png'), (playerSize, playerSize))
cowImg = pygame.transform.scale(pygame.image.load('cow.png'), (cowSize, cowSize))
farmImg = pygame.transform.scale(pygame.image.load('farm.png'), (cowSize, cowSize))
numOfCows = 1
numCaptured = 0
numAlienWins = 0
numCowWins = 0
totalTime = 0 
gameTime = [60, 40, 20]
fastest_times= []
timeSaved= False 

font = pygame.font.Font("raidercrusaderlaser.ttf", 36)
fontBig = pygame.font.Font("raidercrusaderlaser.ttf", 70)
fontSmall = pygame.font.Font("raidercrusaderlaser.ttf", 29)


player_pos = pygame.Vector2(screen_width / 2, 10)
cows = [
    {
        "pos": pygame.Vector2(
            random.randint(0, screen_width - cowSize),
            random.randint(screen_height // 2, screen_height - cowSize)
        ),
        "speed": random.randint(100, 200),
        "direction": pygame.Vector2(random.choice([-1, 1]), 0),
        "selected": False,
        "captured": False,
        "time_since_last_change": 0,
        "time_since_last_jump": 0,
        "time_below": 0
    }
    for _ in range(numOfCows)
]

currentRound=0
game_over = False
win_counted = False 

running = True
while running:
    dt = clock.tick(60) / 1000
    totalTime += dt 
    roundedTime = round(totalTime)
    timeRemaining = max(0, gameTime[currentRound] - roundedTime)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()                
            for cow in cows:
                cow["selected"] = False  
            for cow in cows:
                if not cow["captured"]:
                    cow_rect = pygame.Rect(cow["pos"].x, cow["pos"].y, cowSize, cowSize)
                    if cow_rect.collidepoint(mouse_pos):
                        cow["selected"] = not cow["selected"]

    screen.blit(bg, (0, 0))
    screen.blit(playerImg, (player_pos.x, player_pos.y))
    screen.blit(farmImg, (300, 300))
    farm_rect = pygame.Rect(300, 300, cowSize, cowSize)
    screen.blit(farmImg, (900, 10))
    farm_rect = pygame.Rect(900, 10, cowSize, cowSize)


    if farm_rect.collidepoint(player_pos.x, player_pos.y):
        game_over=True
        print("game_over")
        
    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_pos.x -= 400 * dt
    if keys[pygame.K_RIGHT]:
        player_pos.x += 400 * dt
    if keys[pygame.K_UP]:
        player_pos.y -= 400 * dt
    if keys[pygame.K_DOWN]:
        player_pos.y += 400 * dt

    # player bounds
    player_pos.x = max(0, min(player_pos.x, screen_width - playerSize))
    player_pos.y = max(0, min(player_pos.y, screen_height / 2 - 50))

    margin = 60

    # cows logic
    for cow in cows:
        cow["time_since_last_jump"] += dt

        # abduction 
        if (
            not cow["captured"]
            and player_pos.x - margin <= cow["pos"].x <= player_pos.x + playerSize + margin
        ):
            cow["time_below"] += dt
        else:
            cow["time_below"] = 0

        if cow["time_below"] >= 3:
            cow["captured"] = True
            numCaptured += 1
            cow["time_below"] = 0

        if cow["captured"]:
            cow["pos"].y = player_pos.y
            cow["pos"].x += (player_pos.x + 45 - 40 - cow["pos"].x) * 5 * dt
        else:
            # Wandering 
            if not cow["selected"]:
                cow["time_since_last_change"] += dt
                if cow["time_since_last_change"] >= 2:
                    cow["direction"] = pygame.Vector2(random.choice([-1, 1]), 0)
                    cow["time_since_last_change"] = 0

                cow["pos"] += cow["direction"] * cow["speed"] * dt

            # control for selected cows
            if cow["selected"]:
                if keys[pygame.K_a]:
                    cow["pos"].x -= 600 * dt
                if keys[pygame.K_d]:
                    cow["pos"].x += 600 * dt
                if (keys[pygame.K_SPACE] and cow["time_since_last_change"] > 6):
                    cow["pos"].x = cow["pos"].x + 30
                    cow["time_since_last_jump"] = 0

            # cows bounds
            cow["pos"].x = max(0, min(cow["pos"].x, screen_width - cowSize))
            cow["pos"].y = max(screen_height // 2, min(cow["pos"].y, screen_height - cowSize))

        # load cows and abduction progress
        screen.blit(cowImg, (cow["pos"].x, cow["pos"].y))
        abduction_progress = min(cow["time_below"] / 3, 1)
        progress_bar_width = int(70 * abduction_progress)
        pygame.draw.rect(screen, (255, 0, 0), (cow["pos"].x + 5, cow["pos"].y - 5, progress_bar_width, 8))
        if cow["selected"]:
            pygame.draw.rect(screen, "black", (cow["pos"].x, cow["pos"].y, cowSize, cowSize), 2)

    text = font.render(f'Cows captured: {numCaptured}', True, (255, 0, 0))
    screen.blit(text, (10,10))

    # game over page 
    if (numCaptured == numOfCows or timeRemaining == 0):   
        game_over = True    

        if not timeSaved: 
            completion_time =totalTime 
            completion_time= totalTime
            fastest_times.append(completion_time)
            fastest_times= sorted(fastest_times)[:5]
            timeSaved= True 

        text2 = fontBig.render('GAME OVER', True, (255, 0, 0))
        if not win_counted:
            if numCaptured == numOfCows: 
                numAlienWins += 1
                text3 = fontBig.render('ALIENS WIN', True, (255, 0, 0))
            else: 
                numCowWins += 1
                text3 = fontBig.render('COWS WIN', True, (255, 0, 0))
            win_counted = True
        text4 = font.render('PLAY AGAIN', True, (0, 255, 0))
        text5 = font.render(f'Alien wins: {numAlienWins}', True, (100, 100, 100))
        text7 = font.render(f'Cow wins: {numCowWins}', True, (100, 100, 100))
        screen.blit(bg2, (0, 0))
        screen.blit(text2, (470, 105))
        screen.blit(text3, (470, 175))
        button_rect = pygame.Rect(495, 525, 300, 80)
        pygame.draw.rect(screen, "black", (495, 525, 300, 80), 50)
        screen.blit(text4, (540, 545))
        screen.blit(text5, (30, 30))
        screen.blit(text7, (30, 70))

        for i, time in enumerate(fastest_times):
            leaderText= font.render("Leaderboard:", True, (40,35,100))
            textFastest=fontSmall.render(f"#{i+1}: {time:.2f}s", True, (100,100,100))
            screen.blit(leaderText,(screen_width/2 - 100, screen_height/2 - 50))
            screen.blit(textFastest, (screen_width/2 - 100, screen_height/2 + i * 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if button_rect.collidepoint(mouse_pos):
                    numCaptured = 0
                    totalTime = 0
                    currentRound = (currentRound + 1) % len(gameTime)
                    game_over = False
                    win_counted = False
                    timeRemaining= False 
                    timeSaved = False

                    cows = [
                        {
                            "pos": pygame.Vector2(
                                random.randint(0, screen_width - cowSize),
                                random.randint(screen_height // 2, screen_height - cowSize)
                            ),
                            "speed": random.randint(100, 200),
                            "direction": pygame.Vector2(random.choice([-1, 1]), 0),
                            "selected": False,
                            "captured": False,
                            "time_since_last_change": 0,
                            "time_since_last_jump": 0,
                            "time_below": 0
                        }
                        for _ in range(numOfCows)
                    ]
    
    text8 = font.render(f'Time Remaining: {timeRemaining}', True, (255, 0, 0))
    screen.blit(text8, (screen_width/2 - 115, 10))

    pygame.display.update()
pygame.quit()