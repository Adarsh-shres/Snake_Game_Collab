import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 560, 620
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("STATIC SNAKE")

BG         = (2, 12, 2)
HEAD_COLOR = (175, 255, 202)
BODY_COLOR = (0, 179, 44)
CELL       = 28

snake_body = [(10, 10), (9, 10), (8, 10), (7, 10)]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(BG)

    # Draw Snake
    for i, (cx, cy) in enumerate(snake_body):
        # Convert grid coords to pixels (adding 60px offset for the top area)
        rx, ry = cx * CELL, cy * CELL + 60
        
        # Color the first segment as the head, others as body
        color = HEAD_COLOR if i == 0 else BODY_COLOR
        
        pygame.draw.rect(screen, color, (rx + 1, ry + 1, CELL - 2, CELL - 2))

    pygame.display.flip()