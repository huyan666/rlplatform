import random, pygame, sys, threading
from pygame.locals import *
import numpy as np
import math


class BASEPLANE(pygame.sprite.Sprite):

    def __init__(self, iid, x0, y0, h, r, vel):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load("flight.png")
        self.iid = iid
        self.rect = self.image.get_rect()
        self.vel = vel
        self.x = x0
        self.y = y0
        self.r = r
        self.h = h
        self.rect.center = (self.x, self.y)
        self.hp = 100
        self.direction = math.radians(0)
        self.lock = threading.Lock()
        self.screen = pygame.display.get_surface()

    def update(self):
        self.lock.acquire(timeout=1)
        self.rect.center = (self.x, self.y)
        pygame.draw.circle(self.screen, (255, 0, 0), (round(self.x), round(self.y)), self.r, 1)
        self.lock.release()

    def rotate(self,direction):
        self.image = pygame.transform.rotate(self.image, math.degrees(direction))
        print(self.direction)
        self.rect = self.image.get_rect(center=self.rect.center)
    def moveto(self, action):
        direction=action["DIRECTION"]
        if self.direction !=direction:
            self.rotate(self.direction-direction)
            self.direction = direction

        dx=math.cos(direction)*self.vel
        dy=math.sin(direction)*self.vel
        self.x = self.x + dx
        self.y = self.y + dy

    def setgroup(self, planegroup, staticgroup, dynamicgroup):
        self.staticgroup = staticgroup
        self.dynamicgroup = dynamicgroup
        self.planegroup = planegroup



class AttackPlane(BASEPLANE):

    def __init__(self, iid, x, y, h, r, vel, damage, damagerate):
        super(AttackPlane, self).__init__(iid, x, y, h, r, vel)
        self.damage = damage
        self.damagerate = damagerate
        self.type = "AttackPlane"

    def act(self, action):
        self.moveto(action)
        if action["ATTACK_TYPE"] in ["RADAR", "ADK", "AAG"] and action["ATTACK_ID"] >= 0:
            for i in self.staticgroup.sprites():
                if i.iid == action["ATTACK_ID"]:
                    if random.randint(0, 100) < (self.damagerate * 100):
                        i.hp = i.hp - self.damage
                        if i.hp < 0:
                            i.kill()
        if action["ATTACK_TYPE"] in ["EnemyScoutPlane", "EnemyAttackPlane"] and action["ATTACK_ID"] >= 0:
            for i in self.dynamicgroup.sprites():
                if i.iid == action["ATTACK_ID"]:
                    if random.randint(0, 100) < (self.damagerate * 100):
                        i.hp = i.hp - self.damage
                        if i.hp < 0:
                            i.kill()

    def get_obs(self):
        plan_obs = {}
        plan_obs["ID"] = self.iid
        plan_obs["TYPE"] = self.type
        plan_obs["POS"] = [self.x, self.y, self.h]
        plan_obs["DIRECTION"] = self.direction
        plan_obs["VEL"] = self.vel
        plan_obs["RADIUS"] = self.r
        plan_obs["DAMAGE"] = self.damage
        plan_obs["DAMAGERATE"] = self.damagerate

        threaten_obs = []
        for i in self.staticgroup.sprites():
            dis = ((self.x - i.x) ** 2 + (self.y - i.y) ** 2) ** 0.5
            if dis < self.r:
                static_obs = {}
                static_obs["ID"] = i.iid
                static_obs["TYPE"] = i.type
                static_obs["POS"] = [i.x, i.y, i.h]
                static_obs["RADIUS"] = i.r
                threaten_obs.append(static_obs)
        for i in self.dynamicgroup.sprites():
            dis = ((self.x - i.x) ** 2 + (self.y - i.y) ** 2) ** 0.5
            if dis < self.r:
                dynamic_obs = {}
                dynamic_obs["ID"] = i.iid
                dynamic_obs["TYPE"] = i.type
                dynamic_obs["POS"] = [i.x, i.y, i.h]
                threaten_obs.append(dynamic_obs)
        plan_obs["THREAT"] = threaten_obs
        return plan_obs


class ScoutPlane(BASEPLANE):

    def __init__(self, iid, x, y, h, r, vel):
        super(ScoutPlane, self).__init__(iid, x, y, h, r, vel)
        self.type = "ScoutPlane"

    def act(self, action):
        self.moveto(action)

    def get_obs(self):
        plan_obs = {}
        plan_obs["ID"] = self.iid
        plan_obs["TYPE"] = self.type
        plan_obs["POS"] = [self.x, self.y, self.h]
        plan_obs["DIRECTION"] = self.direction
        plan_obs["VEL"] = self.vel
        plan_obs["RADIUS"] = self.r

        threaten_obs = []
        for i in self.staticgroup.sprites():
            dis = ((self.x - i.x) ** 2 + (self.y - i.y) ** 2) ** 0.5
            if dis < self.r:
                static_obs = {}
                static_obs["ID"] = i.iid
                static_obs["TYPE"] = i.type
                static_obs["POS"] = [i.x, i.y, i.h]
                static_obs["RADIUS"] = i.r
                threaten_obs.append(static_obs)
        for i in self.dynamicgroup.sprites():
            dis = ((self.x - i.x) ** 2 + (self.y - i.y) ** 2) ** 0.5
            if dis < self.r:
                dynamic_obs = {}
                dynamic_obs["ID"] = i.iid
                dynamic_obs["TYPE"] = i.type
                dynamic_obs["POS"] = [i.x, i.y, i.h]
                threaten_obs.append(dynamic_obs)
        plan_obs["THREAT"] = threaten_obs
        return plan_obs


class JammerPlane(BASEPLANE):
    def __init__(self, iid, x, y, h, r, vel):
        super(JammerPlane, self).__init__(iid, x, y, h, r, vel)
        self.type = "JammerPlane"

    def act(self, action, ignoreplaneid):
        self.moveto(action)
        for i in self.planegroup.sprites():
            dis = ((self.x - i.x) ** 2 + (self.y - i.y) ** 2) ** 0.5
            if dis < self.r:
                ignoreplaneid.append(i.iid)

    def get_obs(self):
        plan_obs = {}
        plan_obs["ID"] = self.iid
        plan_obs["TYPE"] = self.type
        plan_obs["POS"] = [self.x, self.y, self.h]
        plan_obs["DIRECTION"] = self.direction
        plan_obs["VEL"] = self.vel
        plan_obs["RADIUS"] = self.r

        threaten_obs = []
        for i in self.staticgroup.sprites():
            dis = ((self.x - i.x) ** 2 + (self.y - i.y) ** 2) ** 0.5
            if dis < self.r:
                static_obs = {}
                static_obs["ID"] = i.iid
                static_obs["TYPE"] = i.type
                static_obs["POS"] = [i.x, i.y, i.h]
                static_obs["RADIUS"] = i.r
                threaten_obs.append(static_obs)
        for i in self.dynamicgroup.sprites():
            dis = ((self.x - i.x) ** 2 + (self.y - i.y) ** 2) ** 0.5
            if dis < self.r:
                dynamic_obs = {}
                dynamic_obs["ID"] = i.iid
                dynamic_obs["TYPE"] = i.type
                dynamic_obs["POS"] = [i.x, i.y, i.h]
                threaten_obs.append(dynamic_obs)
        plan_obs["THREAT"] = threaten_obs
        return plan_obs


class ThermalPlane(BASEPLANE):
    def __init__(self, tid, x, y, h, r, vel):
        super(ThermalPlane, self).__init__(tid, x, y, h, r, vel)
        self.type = "ThermalPlane"

    def act(self, action, attackignplaneid):
        self.moveto(action)
        for i in self.planegroup.sprites():
            dis = ((self.x - i.x) ** 2 + (self.y - i.y) ** 2) ** 0.5
            if dis < self.r and i.iid is not self.iid:
                attackignplaneid.append(i.iid)

    def get_obs(self):
        plan_obs = {}
        plan_obs["ID"] = self.iid
        plan_obs["TYPE"] = self.type
        plan_obs["POS"] = [self.x, self.y, self.h]
        plan_obs["DIRECTION"] = self.direction
        plan_obs["VEL"] = self.vel
        plan_obs["RADIUS"] = self.r

        threaten_obs = []
        for i in self.staticgroup.sprites():
            dis = ((self.x - i.x) ** 2 + (self.y - i.y) ** 2) ** 0.5
            if dis < self.r:
                static_obs = {}
                static_obs["ID"] = i.iid
                static_obs["TYPE"] = i.type
                static_obs["POS"] = [i.x, i.y, i.h]
                static_obs["RADIUS"] = i.r
                threaten_obs.append(static_obs)
        for i in self.dynamicgroup.sprites():
            dis = ((self.x - i.x) ** 2 + (self.y - i.y) ** 2) ** 0.5
            if dis < self.r:
                dynamic_obs = {}
                dynamic_obs["ID"] = i.iid
                dynamic_obs["TYPE"] = i.type
                dynamic_obs["POS"] = [i.x, i.y, i.h]
                threaten_obs.append(dynamic_obs)
        plan_obs["THREAT"] = threaten_obs
        return plan_obs


class EnemyAttackPlane(BASEPLANE):
    def __init__(self, iid, x, y, h, r, vel, damage, damagerate):
        super(EnemyAttackPlane, self).__init__(iid, x, y, h, r, vel)
        self.damage = damage
        self.damagerate = damagerate
        self.type = "EnemyAttackPlane"

    def act(self, action, attackignplaneid):
        self.moveto(action)
        if action["ATTACK_TYPE"] in ["AttackPlane", "ScoutPlane", "JammerPlane", "ThermalPlane"] and action[
            "ATTACK_ID"] >= 0:
            for i in self.planegroup.sprites():
                if i.iid == action["ATTACK_ID"] and i.iid not in attackignplaneid:
                    if random.randint(0, 100) < (self.damagerate * 100):
                        i.hp = i.hp - self.damage
                        if i.hp < 0:
                            i.kill()

    def get_obs(self, ignoreplaneid):
        plan_obs = {}
        plan_obs["ID"] = self.iid
        plan_obs["TYPE"] = self.type
        plan_obs["POS"] = [self.x, self.y, self.h]
        plan_obs["DIRECTION"] = self.direction
        plan_obs["VEL"] = self.vel
        plan_obs["RADIUS"] = self.r
        plan_obs["DAMAGE"] = self.damage
        plan_obs["DAMAGERATE"] = self.damagerate

        threaten_obs = []
        for i in self.planegroup.sprites():
            if i.iid in ignoreplaneid:
                continue
            dis = ((self.x - i.x) ** 2 + (self.y - i.y) ** 2) ** 0.5
            if dis < self.r:
                static_obs = {}
                static_obs["ID"] = i.iid
                static_obs["TYPE"] = i.type
                static_obs["POS"] = [i.x, i.y, i.h]
                threaten_obs.append(static_obs)
        plan_obs["PLANE"] = threaten_obs
        return plan_obs


class EnemyScoutPlane(BASEPLANE):
    def __init__(self, iid, x, y, h, r, vel):
        super(EnemyScoutPlane, self).__init__(iid, x, y, h, r, vel)
        self.type = "EnemyScoutPlane"

    def get_obs(self, ignoreplaneid):
        plan_obs = {}
        plan_obs["ID"] = self.iid
        plan_obs["TYPE"] = self.type
        plan_obs["POS"] = [self.x, self.y, self.h]
        plan_obs["DIRECTION"] = self.direction
        plan_obs["VEL"] = self.vel
        plan_obs["RADIUS"] = self.r

        threaten_obs = []
        for i in self.planegroup.sprites():
            if i.iid in ignoreplaneid:
                continue
            dis = ((self.x - i.x) ** 2 + (self.y - i.y) ** 2) ** 0.5
            if dis < self.r:
                static_obs = {}
                static_obs["ID"] = i.iid
                static_obs["TYPE"] = i.type
                static_obs["POS"] = [i.x, i.y, i.h]
                threaten_obs.append(static_obs)
        plan_obs["PLANE"] = threaten_obs
        return plan_obs

    def act(self, action):
        self.moveto(action)


'''
class PlaneThread(threading.Thread):

    def __init__(self, plane, threatengroup):
        threading.Thread.__init__(self)

        self.plane = plane
        self.threat = threatengroup

    def run(self) -> None:
        while True:
            self.plane.lock.acquire(timeout=1)
            newx, newy = self.GetNextPosition()
            if newx not in range(0, MAPSIZEX) or newy not in range(0, MAPSIZEY):
                self.plane.lock.release()
                continue
            else:
                self.plane.x = newx
                self.plane.y = newy
            self.plane.lock.release()
            for st in self.threat.sprites():
                st.lock.acquire(timeout=1)
                dis = math.sqrt((self.plane.x - st.x) ** 2 + (self.plane.y - st.y) ** 2)
                if (dis < self.plane.r):
                    st.hp = st.hp - self.plane.damage
                    print(self.plane.damage)
                if (st.hp <= 0):
                    st.kill()
                    st.lock.release()
                    continue
                print(st.hp)
                st.lock.release()

            pygame.time.wait(self.plane.vel)

    def GetNextPosition(self):
        # direction=self.plane.direction
        self.plane.direction = random.choice((1, 2, 3, 4))
        if self.plane.direction == 1:
            newx = self.plane.x - self.plane.vel
            newy = self.plane.y
        elif self.plane.direction == 2:
            newx = self.plane.x + self.plane.vel
            newy = self.plane.y
        elif self.plane.direction == 3:
            newx = self.plane.x
            newy = self.plane.y - self.plane.vel
        elif self.plane.direction == 4:
            newx = self.plane.x
            newy = self.plane.y + self.plane.vel
        else:
            assert False
        return newx, newy


def handle_event():
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()


def main():
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURE = pygame.display.set_mode((500, 500))
    pygame.display.set_caption('Test')

    a = BASEPLANE(250, 250, h=10, vel=20, r=50, damage=100, damagerate=0.8)
    b = StaticThreaten(300, 300, 100, 100)

    plangroup = pygame.sprite.Group(a)
    threatengroup = pygame.sprite.Group(b)
    A = PlaneThread(a, threatengroup)

    A.start()

    while True:
        FPSCLOCK.tick(30)
        handle_event()
        DISPLAYSURE.fill((255, 255, 255))
        plangroup.update()
        plangroup.draw(DISPLAYSURE)
        threatengroup.update()
        threatengroup.draw(DISPLAYSURE)
        pygame.display.flip()
'''
