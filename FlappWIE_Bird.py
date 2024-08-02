import cv2
import mediapipe as mp
import pygame
import random

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_drawing = mp.solutions.drawing_utils
    
    def get_hand_position(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                for id, lm in enumerate(hand_landmarks.landmark):
                    h, w, c = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    if id == 8: 
                        return cx, cy, h
        return None

pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Bird")

white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)
purple = (128, 0, 128)

#BIRD
bird_image = pygame.image.load("bird.png")
bird_image = pygame.transform.scale(bird_image, (50, 50))

bird_x = 100
bird_y = 300
bird_width = 50
bird_height = 50
score = 0

#PIPES
pipe_width = 80
pipe_gap = 200
pipe_velocity = 5  
pipes = []
pipe_distance = 300 

#GAME FUNCTIONS
def draw_bird(x, y):
    screen.blit(bird_image, (x, y))

def draw_pipes(pipes):
    for pipe in pipes:
        pygame.draw.rect(screen, purple, pipe['top'])
        pygame.draw.rect(screen, purple, pipe['bottom'])

def move_pipes(pipes):
    for pipe in pipes:
        pipe['top'].x -= pipe_velocity
        pipe['bottom'].x -= pipe_velocity

def generate_pipes():
    height = random.randint(200, 400)
    top_pipe = pygame.Rect(screen_width, 0, pipe_width, height)
    bottom_pipe = pygame.Rect(screen_width, height + pipe_gap, pipe_width, screen_height - height - pipe_gap)
    pipes.append({'top': top_pipe, 'bottom': bottom_pipe, 'scored': False})

def calculate_pipe_distance(base_distance, velocity, factor=0.5):
    return base_distance + (velocity ** factor)

def check_collision(bird_rect, pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe['top']) or bird_rect.colliderect(pipe['bottom']):
            return True
    return False

def update_score(bird_rect, pipes):
    global score, pipe_velocity
    for pipe in pipes:
        if pipe['top'].right < bird_rect.left and not pipe['scored']:
            score += 1
            pipe['scored'] = True
            print(f"Score: {score}")
            #PIPE VELOCITY ADJUSTMENT
            if score % 2 == 0:
                pipe_velocity += 1

#MAIN FUNC
def game_loop():
    global bird_y, score, pipe_velocity, pipe_distance
    
    hand_tracker = HandTracker()
    cap = cv2.VideoCapture(0)
    clock = pygame.time.Clock()
    run = True
    frame_count = 0
    
    #BASE DIST
    base_pipe_distance = 300

    while run:
        ret, frame = cap.read()
        if not ret:
            break
        
        hand_pos = hand_tracker.get_hand_position(frame)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        if hand_pos:
            _, hand_y, frame_height = hand_pos
            bird_y = (hand_y / frame_height) * screen_height - bird_height // 2
        
        bird_rect = pygame.Rect(bird_x, bird_y, bird_width, bird_height)
        
        if len(pipes) == 0 or pipes[-1]['top'].x < screen_width - pipe_distance:
            generate_pipes()
            pipe_distance = calculate_pipe_distance(base_pipe_distance, pipe_velocity)

        move_pipes(pipes)
        pipes[:] = [pipe for pipe in pipes if pipe['top'].right > 0]
        
        if check_collision(bird_rect, pipes):
            run = False
        
        update_score(bird_rect, pipes)
        
        screen.fill(white)
        draw_bird(bird_x, bird_y)
        draw_pipes(pipes)
        
        score_text = pygame.font.SysFont(None, 55).render(f"Score: {score}", True, black)
        screen.blit(score_text, (10, 10))
        
        pygame.display.update()
        clock.tick(30)
        frame_count += 1
    
    cap.release()
    pygame.quit()
    cv2.destroyAllWindows()

game_loop()
