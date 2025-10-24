"""
platformer.py

Bibliothèque d'objets réutilisables pour un jeu de plateformes 2D (inspiré de Super Mario)
Écrit en Python + pygame.

Ce module NE crée PAS de niveau. Il fournit des classes et fonctions:
  - GameObject (base)
  - Player
  - Platform (statique)
  - MovingPlatform
  - OneWayPlatform
  - Coin
  - Enemy (patrouille simple)
  - Camera (groupe de sprites avec offset)
  - make_placeholder_sprite(label, size, color)

Utilisez ces classes pour construire vos propres niveaux ailleurs.

Dépendances: pygame
Installer: pip install pygame

Exemples d'utilisation sont fournis dans la docstring de chaque classe mais rien n'est créé automatiquement
parce que vous avez demandé explicitement: *ne crée pas de niveau*. 

Auteur: généré par ChatGPT
"""

import pygame
from pygame import Rect
from typing import Tuple, Optional

# ---- Configuration de base ------------------------------------------------
TILE = 32  # taille par défaut des tiles / sprites
GRAVITY = 100  # pixels / s^2
TERMINAL_V = 800  # vitesse de chute max

# ---- Utilitaires ----------------------------------------------------------

import os

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

def load_image(name, size=None):
    path = os.path.join(ASSET_DIR, name)
    image = pygame.image.load(path).convert_alpha()
    if size:
        image = pygame.transform.scale(image, size)
    return image

def tile_image(texture, width, height):
    """Répète une texture sur une surface de taille donnée."""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    tw, th = texture.get_size()
    for x in range(0, width, tw):
        for y in range(0, height, th):
            surface.blit(texture, (x, y))
    return surface

def make_placeholder_sprite(label: str, size: Tuple[int, int], color: Tuple[int, int, int]):
    """Crée une Surface servant de sprite placeholder.
    label: texte affiché centré (ex: 'PLAYER', 'PLAT').
    size: (w, h) en pixels.
    color: (r,g,b).
    Retourne: pygame.Surface
    """
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill(color)
    try:
        font = pygame.font.Font(None, max(12, size[1] // 3))
        text = font.render(label, True, (255, 255, 255))
        tr = text.get_rect(center=(size[0] // 2, size[1] // 2))
        surf.blit(text, tr)
    except Exception:
        # Dans des environnements sans font, on ignore le texte
        pass
    return surf

# ---- Base: GameObject -----------------------------------------------------
class GameObject(pygame.sprite.Sprite):
    """Base pour tous les objets du jeu.

    Propriétés importantes:
      - self.rect: Rect positionnel
      - self.vx, self.vy: vitesses en pixels/sec
      - self.solid: si True, participe aux collisions de plateforme

    NOTE: les collisions se font par test AABB via rect.
    """
    def __init__(self, x: float, y: float, image: pygame.Surface):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(int(x), int(y)))
        self.vx = 0.0
        self.vy = 0.0
        self.solid = True

    def update(self, dt: float, world: Optional[dict] = None):
        """Mettre à jour l'objet.
        dt: delta-time en secondes.
        world: dictionnaire facultatif contenant des groupes/infos (ex: {'platforms': Group})
        """
        # Mouvement basique
        self.rect.x += int(self.vx * dt)
        self.rect.y += int(self.vy * dt)

# ---- Plateformes ---------------------------------------------------------
class Platform(GameObject):
    """Plateforme statique simple.

    Constructeur:
        Platform(x, y, w, h, color=(100,100,100))
    """
    def __init__(self, x: float, y: float, w: int, h: int, color: Tuple[int, int, int] = (100,100,100), image = None):
        if image:
            img = image
        else:
            img = make_placeholder_sprite('PLAT', (w, h), color)
        super().__init__(x, y, img)
        self.solid = True

class OneWayPlatform(Platform):
    """Plateforme marchable uniquement quand le joueur tombe dessus (one-way).
    La logique d'acceptation du contact doit être gérée depuis la détection de collisions
    du Player (voir méthodes utilitaires dans Player).
    """
    def __init__(self, x, y, w, h, color=(120, 90, 60)):
        super().__init__(x, y, w, h, color)
        self.type = 'oneway'

class MovingPlatform(Platform):
    """Plateforme se déplaçant entre deux points.

    args: path=((x1,y1),(x2,y2)), speed pixels/sec, loop True/False
    """
    def __init__(self, x, y, w, h, path: Tuple[Tuple[int,int], Tuple[int,int]], speed: float=100.0, color=(80,120,200)):
        super().__init__(x, y, w, h, color)
        self.path = [pygame.math.Vector2(p) for p in path]
        self.speed = speed
        self._target = 1
        self.pos = pygame.math.Vector2(x, y)
        self.solid = True

    def update(self, dt: float, world: Optional[dict] = None):
        if len(self.path) < 2:
            return
        target_pos = self.path[self._target]
        dir_vec = (target_pos - self.pos)
        dist = dir_vec.length()
        if dist < 1e-6:
            # switch
            self._target = (self._target + 1) % len(self.path)
            return
        move = dir_vec.normalize() * self.speed * dt
        if move.length() >= dist:
            self.pos = target_pos
            self._target = (self._target + 1) % len(self.path)
        else:
            self.pos += move
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))

# ---- Collectibles -------------------------------------------------------
class Coin(GameObject):
    """Pièce ramassable. Quand on appelle collect(), elle s'enlève du groupe.

    coin.collect() -> return valeur (int)
    """
    def __init__(self, x, y, value: int = 1, image = None):
        if image:
            img = image
        else:
            img = make_placeholder_sprite('COIN', (TILE//2, TILE//2), (220,180,0))
        super().__init__(x, y, img)
        self.value = value
        self.solid = False

    def collect(self):
        # Par défaut retourne la valeur et kill() l'objet pour être retiré des groupes
        try:
            self.kill()
        except Exception:
            pass
        return self.value

# ---- Ennemi simple ------------------------------------------------------
class Enemy(GameObject):
    """Ennemi patrouillant horizontalement entre deux bornes.

    enemy = Enemy(x, y, w, h, patrol=(x1,x2), speed)
    """
    def __init__(self, x, y, w: int, h: int, patrol: Tuple[int,int], speed: float = 60.0, color=(200,50,50), image=None):
        if image:
            img = image
        else:
            img = make_placeholder_sprite('ENEMY', (w, h), color)
        super().__init__(x, y, img)
        self.patrol = patrol
        self.speed = speed
        self.direction = 1
        self.vx = speed
        self.solid = True

    def update(self, dt: float, world: Optional[dict] = None):
        self.rect.x += int(self.vx * dt)
        if self.rect.left < min(self.patrol):
            self.rect.left = min(self.patrol)
            self.vx = abs(self.speed)
        elif self.rect.left > max(self.patrol):
            self.rect.left = max(self.patrol)
            self.vx = -abs(self.speed)

# ---- Player -------------------------------------------------------------
class Player(GameObject):
    """Classe Player avec physiques simples (accélération, saut, collisions AABB).

    Contrôles attendus par défaut: gauche/droite/jump (à gérer côté jeu).

    Méthodes importantes:
      - apply_input(left_bool, right_bool, jump_pressed_bool, jump_held_bool, dt)
      - resolve_collisions(platforms_group)

    Le jeu appelant doit gérer l'input et fournir les groupes de plateformes/coins/enemies.
    """
    def __init__(self, x: float, y: float, w: int = TILE, h: int = TILE*2, color: Tuple[int,int,int]=(50,150,50), image = None):
        if image:
            img = image
        else:
            img = make_placeholder_sprite('PLAYER', (w, h), color)
        super().__init__(x, y, img)
        # Movement
        self.speed = 20.0  # pixels/sec horizontal max
        self.accel = 100.0  # accel
        self.friction = 100.0
        self.jump_speed = 20.0
        self.can_double_jump = False
        self.jumps_left = 1
        # State
        self.on_ground = False
        self.solid = True

    def apply_input(self, left: bool, right: bool, jump_pressed: bool, jump_held: bool, dt: float):
        # Horizontal accel
        desired_vx = 0
        if left and not right:
            desired_vx = -self.speed
        elif right and not left:
            desired_vx = self.speed
        # Simple approach: accelerate towards desired_vx
        if self.vx < desired_vx:
            self.vx = min(desired_vx, self.vx + self.accel * dt)
        elif self.vx > desired_vx:
            self.vx = max(desired_vx, self.vx - self.accel * dt)

        # Gravity
        self.vy += GRAVITY * dt
        if self.vy > TERMINAL_V:
            self.vy = TERMINAL_V

        # Jump
        if jump_pressed:
            if self.on_ground or self.jumps_left > 0:
                self.vy = -self.jump_speed
                if not self.on_ground:
                    self.jumps_left -= 1
                self.on_ground = False

        # Variable jump height: if jump released while moving up, reduce vy
        if not jump_held and self.vy < 0:
            self.vy += GRAVITY * 0.4 * dt  # drag upwards

        # Apply movement
        self.rect.x += self.vx * dt
        self.rect.y += self.vy * dt
        self.rect.x = int(self.rect.x)
        self.rect.y = int(self.rect.y)

    def resolve_collisions(self, platforms: pygame.sprite.Group):
        """Résout les collisions avec les plateformes, proprement et sans glitchs."""
        # --- Mouvement horizontal ---
        self.rect.x += int(self.vx)
        hits = pygame.sprite.spritecollide(self, platforms, dokill=False)
        for p in hits:
            if not p.solid:
                continue
            # Collision droite
            if self.vx > 0 and self.rect.right > p.rect.left:
                self.rect.right = p.rect.left
                self.vx = 0
            # Collision gauche
            elif self.vx < 0 and self.rect.left < p.rect.right:
                self.rect.left = p.rect.right
                self.vx = 0

        # --- Mouvement vertical ---
        self.rect.y += int(self.vy)
        self.on_ground = False
        hits = pygame.sprite.spritecollide(self, platforms, dokill=False)
        for p in hits:
            if not p.solid:
                continue

            # Cas spécial : plateformes one-way (marchables que du dessus)
            if hasattr(p, "type") and getattr(p, "type") == "oneway":
                # On ne bloque que si on descend et qu'on arrive d'au-dessus
                if self.vy <= 0:
                    continue
                if self.rect.bottom - self.vy > p.rect.top:
                    continue

            # Si on tombe et qu'on touche le haut de la plateforme
            if self.vy > 0 and self.rect.bottom > p.rect.top and self.rect.top < p.rect.top:
                self.rect.bottom = p.rect.top
                self.vy = 0
                self.on_ground = True
                self.jumps_left = 1
            # Si on monte et qu'on touche un plafond
            elif self.vy < 0 and self.rect.top < p.rect.bottom and self.rect.bottom > p.rect.bottom:
                self.rect.top = p.rect.bottom
                self.vy = 0

# ---- Camera / Drawing helpers -------------------------------------------
class CameraGroup(pygame.sprite.Group):
    """Groupe de sprites qui applique un offset (camera) lors du dessin.

    Utilisation:
      cam = CameraGroup(width, height)
      cam.add(sprites...)
      cam.draw(surface, camera_pos=(camx, camy))
    """
    def __init__(self, screen_w: int, screen_h: int):
        super().__init__()
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.camera_pos = pygame.math.Vector2(0, 0)

    def set_center(self, x: float, y: float):
        # centre la caméra autour de x,y
        self.camera_pos.x = x - self.screen_w // 2
        self.camera_pos.y = y - self.screen_h // 2

    def draw(self, surface: pygame.Surface, *args, **kwargs):
        # Dessine tous les sprites avec l'offset camera
        for spr in sorted(self.sprites(), key=lambda s: getattr(s, 'rect').bottom):
            offset_rect = spr.rect.copy()
            offset_rect.x -= int(self.camera_pos.x)
            offset_rect.y -= int(self.camera_pos.y)
            surface.blit(spr.image, offset_rect)

# ---- Helpers pour niveaux (Factories) -----------------------------------

def make_ground_segment(x: int, y: int, length_tiles: int) -> Platform:
    """Crée une plateforme continue de length_tiles * TILE"""
    return Platform(x, y, length_tiles * TILE, TILE)

# ---- Fin du module: AUCUN main loop n'est exécuté ------------------------

# Vous pouvez utiliser ces classes depuis un autre script. Exemple (non exécuté ici):
#
# from platformer import Player, Platform, Coin, MovingPlatform, CameraGroup
# import pygame
#
# screen = pygame.display.set_mode((800, 600))
# player = Player(100, 100)
# ground = Platform(0, 500, 2000, 32)
# coin = Coin(200, 450)
# all_sprites = pygame.sprite.Group(player, ground, coin)
# platforms = pygame.sprite.Group(ground)
# cam = CameraGroup(800, 600)
# cam.add(all_sprites)
#
# # Dans la boucle principale, appelez player.apply_input(...) puis player.resolve_collisions(platforms)
# # puis cam.set_center(player.rect.centerx, player.rect.centery) et cam.draw(screen)

# Fin du fichier