import time
import pygame
import random
import pygame.gfxdraw
import math
import numpy as np

# initier les composants
pygame.init()  # pygame
pygame.font.init()  # textes

# définir les variables

GRAVITY = 0.3  # la gravité
screen = pygame.display.set_mode((1080, 1920))  # l'écran
clock = pygame.time.Clock()  # les fps
basicFont = pygame.font.SysFont("arialblack", 60)  # La police basique
pointFont = pygame.font.SysFont("arialblack", 30)  # la police de texte
titleTextContent = "BouncingBall"  # le titre affiché dans la vidéo

# les variables de texte

titleText = basicFont.render(titleTextContent, True, (255, 255, 255))


# créer la class relative à la balle

class Ball:
    def __init__(self, color, x, y, radius, identity: bool):  # principaux arguments
        self.x = x  # position x
        self.y = y  # position y
        self.color = color  # couleur
        self.radius = radius  # rayon de la balle
        self.vectorX = random.uniform(-10, 10)  # le vecteur force X
        self.vectorY = 0  # Le vecteur force y
        self.score = 0  # le score de la balle
        self.trail = []  # la possition parcourue par la balle
        self.gravityVariation = 0
        self.lastBounce = pygame.time.get_ticks()
        self.lastTimeWinPoint = 0
        self.identity = identity
        self.addPointAutorisation = True
        self.isPassed = False
        self.isPassedTime = 0
        self.reSpawnDelay = 90

    def draw(self):  # dessiner la balle à l'écran
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def move(self):  # bouger la balle à l'écran
        self.vectorY += GRAVITY + self.gravityVariation  # appliquer la gravité

        # metre à jour la possition de la balle
        self.x += self.vectorX
        self.y += self.vectorY

        # enregistrer la possition
        self.trail.append((self.x, self.y))

        # ne garder que les 15 dernière possition
        if len(self.trail) > 15:
            self.trail.pop(0)

        # metre à jour la trainée
        self.drawTrainee()

    def changeScore(self, variation):
        if self.addPointAutorisation:
            self.score = self.score + variation
            if self.identity:  # si la balle est la verte
                greenText.UpdateTextContent(f"YES : {self.score}")

            else:
                redText.UpdateTextContent(f"No : {self.score}")
            self.addPointAutorisation = False
            self.isPassed = True
            self.isPassedTime = self.reSpawnDelay

    def checkBounce(self):
        bx, by = self.x, self.y
        cx, cy = width / 2, height / 2

        distance = math.hypot(bx - cx, by - cy) + self.radius  # distance entre balle et cercle

        if distance >= 300:
            return True
        else:
            return False

    def bounce(self, circle_center):
        # obtenir la normale de la balle
        dx = self.x - circle_center[0]
        dy = self.y - circle_center[1]

        # calculer la distance entre les deux cercle
        distance = math.hypot(dx, dy)

        if distance > 315:
            return

        # éviter la division par 0 si la balle est au centre du cercle
        if distance == 0:
            return

        # normaliser la normale
        nx = dx / distance
        ny = dy / distance

        # extraire le vecteur vitesse actuel (la direction de la balle)
        vx = self.vectorX
        vy = self.vectorY

        # produit scalaire du vecteur vitesse sur la normale
        dot = vx * nx + vy * ny

        # appliquer la réflextion du vecteur vitesse
        self.vectorX = (vx - 2 * dot * nx)
        self.vectorY = (vy - 2 * dot * ny)

        # vérifier que la balle ne se colle bas à l'un des bords et que si oui la débugger
        currentTime = pygame.time.get_ticks()  # obtenir le temps
        deltaTime = currentTime - self.lastBounce  # faire la variation pour comparer

        if deltaTime < 100 and abs(self.vectorY) < 2:  # si inférieur à 100ms et valeur absolue de vecteurY < 2 (lent)
            self.vectorY -= 5  # appliquer une petite poussé vers le haut
            print("Correction de la trajectoire")

        self.lastBounce = currentTime  # metre à jour le dernier rebont

    def calculAngle(self, center_x, center_y):
        dx = self.x - center_x
        dy = self.y - center_y

        # calcul de l'angle en radians
        angle = math.atan2(dy, dx)

        # le passer en degrès
        angle = math.degrees(angle)

        # normaliser l'angle
        if angle < 0:
            angle = angle + 360

        return angle

    def checkIfNeedBreakWithAngle(self, start_angle, stop_angle):
        angle = self.calculAngle(width / 2,
                                 height / 2)  # calculer l'angle de la balle par raport avec le centre du cercle

        if start_angle < stop_angle:  # si l'arc est plein ici
            return start_angle <= angle <= stop_angle
        else:  # si l'arc est vide ici
            return angle >= start_angle or angle <= stop_angle

    def drawTrainee(self):
        for i, (tx, ty) in enumerate(self.trail):  # pour chaque possition
            alpha = int(255 * (i + 1) / len(self.trail))  # opacité progressive
            radius = int(self.radius * (i + 1) / len(self.trail))  # rayon plus petit
            trail_color = (*self.color[:3], alpha)  # couleur avec transparence

            # dessiner un cercle semi-transparent (nécessite surface temporaire)
            trail_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, trail_color, (radius, radius), radius)
            screen.blit(trail_surface, (tx - radius, ty - radius))

    def update(self):
        if not self.addPointAutorisation:  # si l'on ne peut plus ajouter un point

            self.lastTimeWinPoint += 1  # ajouter 1

            if self.lastTimeWinPoint >= 120:  # vérifier si il s'est passé 1 seconde ou plus
                if not self.checkBounce():  # si la balle n'est pas sortie du cercle
                    self.lastTimeWinPoint = 0  # rénitialiser la variable
                    self.addPointAutorisation = True  # autoriser à gagner un point

        if self.checkBounce():

            if self.checkIfNeedBreakWithAngle(arc.startAngle, arc.stopAngle):  # si la balle doit rebondir
                self.bounce(center)

            else:  # procédure si la balle passe à travers l'arc de cercle
                if self.addPointAutorisation:  # si l'on peut gagner un point
                    self.changeScore(1)  # ajouter un point
                    print("Point ajouté")  # confirmer

        if self.isPassed:
            if self.isPassedTime <= 0:
                self.positionCenter()
                self.vectorX = random.uniform(-10, 10)  # pour redonner un mouvement
                self.vectorY = 0
                self.isPassed = False
            else:
                self.isPassedTime -= 1

    def slowModifieGravityVector(self):
        if self.gravityVariation != 0:  # regarder si la gravité à déja été varié
            self.gravityVariation = 0  # remetre normalement
        else:  # dans le cas contraire varier la gravité
            self.gravityVariation = random.uniform(0.1, 0.5)

    def positionCenter(self):
        self.x = width // 2
        self.y = height // 2


class Arc:
    def __init__(self, x, y, color, radius, start_angle, stop_angle):
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.startAngle = start_angle
        self.stopAngle = stop_angle

    def draw(self):
        pygame.gfxdraw.arc(screen, int(self.x), int(self.y), self.radius, self.startAngle, self.stopAngle, self.color)

    def rotate(self):
        aditionAngle = self.stopAngle - self.startAngle

        # nouvelle valeur de l'angle de fin
        if self.stopAngle == 360:
            self.stopAngle = 0
        else:
            self.stopAngle = self.stopAngle + 1

        # nouvelle valeur de l'angle de départ
        if self.startAngle == 360:
            self.startAngle = 0
        else:
            self.startAngle = self.startAngle + 1


class PointText:
    def __init__(self, text_content, color, center_text, antilias: bool):
        self.textContent = text_content
        self.color = color
        self.center = center_text
        self.antilias = antilias
        self.text = pointFont.render(self.textContent, self.antilias, self.color)

    def updateParameters(self):
        self.text = pointFont.render(self.textContent, self.antilias, self.color)

    def draw(self):
        rect = self.text.get_rect(center=self.center)  # préparer le rect
        screen.blit(self.text, rect)  # afficher le texte

    def changeColor(self, color):
        self.color = color
        self.updateParameters()

    def UpdateTextContent(self, text: str):
        self.textContent = text
        self.updateParameters()


# obtenir les dimmension de l'écran
width, height = screen.get_size()
centerWith = width / 2
centerHeight = height / 2

# définir les deux balles

red_ball = Ball((255, 0, 0), width / 2, height / 2, 20, False)
green_ball = Ball((0, 255, 0), width / 2, height / 2, 20, True)

# variable de possitionement des textes de points
greenTextCenter = ((width // 4), (height // 3 + 80))
redTextCenter = ((width // 4 * 3), (height // 3 + 80))

# définir les texte de score
greenText = PointText("YES : 0", (0, 255, 0), greenTextCenter, True)
redText = PointText("No : 0", (255, 0, 0), redTextCenter, True)

# créer l'arc de cercle

arc = Arc(int(width / 2), int(height / 2), (255, 255, 255), 300, 0, 330)

# définir la boucle while

running = True  # variable conditionelle

while running:  # placement de while
    for event in pygame.event.get():  # obtenir tout les évènements
        if event.type == pygame.QUIT:  # quitter si demandé
            running = False

    # définir la variable de possitionement central
    center = (width / 2, height / 2)

    # Effacer l'écran
    screen.fill((0, 0, 0))

    # Déplacer et dessiner la balle verte
    green_ball.move()
    green_ball.draw()

    # Déplacer et dessiner la balle rouge
    red_ball.move()
    red_ball.draw()

    # regarder les angle
    red_ball.checkIfNeedBreakWithAngle(arc.startAngle, arc.stopAngle)
    green_ball.checkIfNeedBreakWithAngle(arc.startAngle, arc.stopAngle)

    # occasionellement modifier légèrement la gravité des balles
    red_ball.slowModifieGravityVector()
    green_ball.slowModifieGravityVector()

    # metre à jour les balles
    red_ball.update()
    green_ball.update()

    # tourner l'arc de cercle
    arc.rotate()

    # dessiner l'arc de cercle
    arc.draw()

    # afficher les textes

    # titre
    text_rect = titleText.get_rect(center=center)
    screen.blit(titleText, text_rect)

    # textes de points
    redText.draw()
    greenText.draw()

    # Mettre à jour l'affichage
    pygame.display.flip()

    # Limiter les FPS
    clock.tick(60)

pygame.quit()