"""
demo_platformer.py

Petite démo utilisant platformer.py — montre comment initialiser une fenêtre, créer
quelques objets, et déplacer le joueur avec les touches fléchées + Espace.

⚠️ Nécessite pygame et platformer.py dans le même dossier.

Contrôles :
  ← →  : se déplacer
  ESPACE : sauter
  ÉCHAP : quitter
"""

import pygame
from platformer import Player, Platform, Coin, MovingPlatform, OneWayPlatform, Enemy, CameraGroup, TILE, load_image, tile_image

pygame.init()

# --- Config écran ---
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Démo Platformer")

# --- Groupes ---
all_sprites = CameraGroup(WIDTH, HEIGHT)
platforms = pygame.sprite.Group()
coins = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# --- Création d'objets ---
player_texture = load_image("mario.png", (TILE, TILE * 2))
player = Player(100, -50, image=player_texture)

# Sol et plateformes
sol_texture = load_image("ground.png", (TILE, TILE))
brique_texture = load_image("brick.png", (TILE, TILE))
bloc_texture = load_image("block.png", (TILE, TILE))
tuyau2_texture = load_image("pipe.png", (TILE * 2, TILE * 2))
tuyau3_texture = load_image("pipe.png", (TILE * 2, TILE * 3))
tuyau4_texture = load_image("pipe.png", (TILE * 2, TILE * 4))
drapeau_texture = load_image("flag.png", (TILE * 2, TILE * 11))
sol1 = Platform(0, 0, TILE * 69, TILE * 2, image = tile_image(sol_texture, TILE * 69, TILE * 2))
sol2 = Platform(TILE * 71, 0, TILE * 15, TILE * 2, image = tile_image(sol_texture, TILE * 15, TILE * 2))
sol3 = Platform(TILE * 89, 0, TILE * 64, TILE * 2, image = tile_image(sol_texture, TILE * 64, TILE * 2))
sol4 = Platform(TILE * 153, 0, TILE * 69, TILE * 2, image = tile_image(sol_texture, TILE * 69, TILE * 2))
bloc1 = Platform(TILE * 16, TILE * -4, TILE, TILE, image=bloc_texture)
brique1 = Platform(TILE * 20, TILE * -4, TILE, TILE, image=brique_texture)
bloc2 = Platform(TILE * 21, TILE * -4, TILE, TILE, image=bloc_texture)
brique2 = Platform(TILE * 22, TILE * -4, TILE, TILE, image=brique_texture)
bloc3 = Platform(TILE * 23, TILE * -4, TILE, TILE, image=bloc_texture)
brique3 = Platform(TILE * 24, TILE * -4, TILE, TILE, image=brique_texture)
bloc4 = Platform(TILE * 22, TILE * -8, TILE, TILE, image=bloc_texture)
tuyau1 = Platform(TILE * 28, TILE * -2, TILE * 2, TILE * 2, image=tuyau2_texture)
tuyau2 = Platform(TILE * 38, TILE * -3, TILE * 2, TILE * 3, image=tuyau3_texture)
tuyau3 = Platform(TILE * 46, TILE * -4, TILE * 2, TILE * 4, image=tuyau4_texture)
tuyau4 = Platform(TILE * 57, TILE * -4, TILE * 2, TILE * 4, image=tuyau4_texture)
drapeau = Platform(TILE * 64, TILE * -11, TILE * 2, TILE * 11, image=drapeau_texture)
oneway = OneWayPlatform(500, 350, 200, 20)

# Pièces et ennemis
goomba_texture = load_image("goomba.png", (TILE, TILE))
coin_texture = load_image("coin.png", (TILE, TILE))
coin1 = Coin(250, 0, image=coin_texture)
coin2 = Coin(520, TILE * -1, image=coin_texture)
enemy1 = Enemy(TILE * 22, TILE * -1, TILE, TILE, patrol=(TILE * 22, 0), speed=60, image=goomba_texture)
enemy2 = Enemy(TILE * 40, TILE * -1, TILE, TILE, patrol=(TILE * 40, TILE * 45), speed=60, image=goomba_texture)
enemy3 = Enemy(TILE * 51, TILE * -1, TILE, TILE, patrol=(TILE * 48, TILE * 56), speed=60, image=goomba_texture)
enemy4 = Enemy(TILE * 52.5, TILE * -1, TILE, TILE, patrol=(TILE * 48, TILE * 56), speed=60, image=goomba_texture)

# Ajout aux groupes
for obj in [player, sol1, sol2, sol3, sol4, bloc1, bloc2, bloc3, bloc4, brique1, brique2, brique3, tuyau1, tuyau2, tuyau3, tuyau4, drapeau, oneway, coin1, coin2, enemy1, enemy2, enemy3, enemy4]:
    all_sprites.add(obj)

for p in [sol1, sol2, sol3, sol4, bloc1, bloc2, bloc3, bloc4, brique1, brique2, brique3, tuyau1, tuyau2, tuyau3, tuyau4, drapeau, oneway]:
    platforms.add(p)
for c in [coin1, coin2]:
    coins.add(c)
for e in [enemy1, enemy2, enemy3, enemy4]:
    enemies.add(e)

# --- Boucle principale ---
running = True
score = 0
while running:
    dt = clock.tick(60) / 1000.0  # secondes

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    keys = pygame.key.get_pressed()
    left = keys[pygame.K_LEFT] or keys[pygame.K_a]
    right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
    jump_pressed = keys[pygame.K_SPACE]

    # --- Update logique ---
    player.apply_input(left, right, jump_pressed, jump_pressed, dt)

    for obj in all_sprites:
        if hasattr(obj, 'update'):
            obj.update(dt, world={'platforms': platforms})

    player.resolve_collisions(platforms)

    # Collecte de pièces
    collected = pygame.sprite.spritecollide(player, coins, dokill=True)
    for c in collected:
        score += c.value

    # Collisions ennemis (simple reset de position)
    if pygame.sprite.spritecollideany(player, enemies):
        player.rect.topleft = (100, -50)
        player.vx = player.vy = 0

    # --- Caméra ---
    all_sprites.set_center(player.rect.centerx, player.rect.centery)

    # --- Rendu ---
    screen.fill((80, 160, 220))
    all_sprites.draw(screen)

    # HUD score
    font = pygame.font.Font(None, 36)
    txt = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(txt, (10, 10))

    pygame.display.flip()

pygame.quit()
