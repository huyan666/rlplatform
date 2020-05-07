import random, pygame, sys, threading
from pygame.locals import *
import numpy as np
import math

from PLANESPRITE import *
from STATICTHREATEN import *


class ENVIROMENT:

    def __init__(self, x, y, attacknums, scoutnums, jammernums, thermalnums, radarnums, adknums, aagnums, dynamicnums):
        self.mapsize_x = x
        self.mapsize_y = y

        self.attacknums = attacknums
        self.scoutnums = scoutnums
        self.jammernums = jammernums
        self.thermalnums = thermalnums

        self.radarnums = radarnums
        self.adknums = adknums
        self.aagnums = aagnums
        self.dynamicnums = dynamicnums

        self.planegroup = pygame.sprite.Group()
        self.staticgroup = pygame.sprite.Group()
        self.dynamicgroup = pygame.sprite.Group()

        pygame.init()
        self.FPSCLOCK = pygame.time.Clock()
        self.DISPLAYSURE = pygame.display.set_mode((self.mapsize_x, self.mapsize_y))
        pygame.display.set_caption('Test')

        self.ignoreplaneid = []  # 侦察忽略的飞机
        self.attackignplaneid = []  # 攻击忽略的飞机
        planeid = 0
        for i in range(self.attacknums):
            x = random.randint(0, self.mapsize_x)
            y = random.randint(0, self.mapsize_y)
            # AttackPlane(self, id, x, y, r, h, vel, damage, damagerate):
            a = AttackPlane(planeid, x, y, 20, 10, 10, 100, 0.8)
            planeid += 1
            self.planegroup.add(a)

        for i in range(self.scoutnums):
            x = random.randint(0, self.mapsize_x)
            y = random.randint(0, self.mapsize_y)
            # AttackPlane(self, id, x, y, r, h, vel, damage, damagerate):
            a = ScoutPlane(planeid, x, y, 20, 10, 10)
            planeid += 1
            self.planegroup.add(a)

        for i in range(self.jammernums):
            x = random.randint(0, self.mapsize_x)
            y = random.randint(0, self.mapsize_y)
            # AttackPlane(self, id, x, y, r, h, vel, damage, damagerate):
            a = JammerPlane(planeid, x, y, 20, 10, 10)
            planeid += 1
            self.planegroup.add(a)

        for i in range(self.attacknums):
            x = random.randint(0, self.mapsize_x)
            y = random.randint(0, self.mapsize_y)
            # AttackPlane(self, id, x, y, r, h, vel, damage, damagerate):
            a = ThermalPlane(planeid, x, y, 20, 10, 10)
            planeid += 1
            self.planegroup.add(a)

        staticid = 0
        for i in range(self.radarnums):
            x = random.randint(0, self.mapsize_x)
            y = random.randint(0, self.mapsize_y)
            b = RADAR(staticid, x, y, 1000, 100)
            staticid += 1
            self.staticgroup.add(b)
        for i in range(self.adknums):
            x = random.randint(0, self.mapsize_x)
            y = random.randint(0, self.mapsize_y)
            # __init__(self, iid, x, y, hp, r, hmax, hmin, dmax, dmin, damage):
            b = ADK(staticid, x, y, 100, 27, 27, 0.015, 80, 0.015, 1000)
            staticid += 1
            self.staticgroup.add(b)
        # for i in range(self.dynamicgroup):
        for i in range(self.aagnums):
            x = random.randint(0, self.mapsize_x)
            y = random.randint(0, self.mapsize_y)
            # __init__(self, iid, x, y, hp, r, hmax, hmin, dmax, dmin, damage):
            b = AAG(staticid, x, y, 100, 20, 15, 20, 500)
            staticid += 1
            self.staticgroup.add(b)

        for i in self.planegroup.sprites():
            i.setgroup(self.planegroup, self.staticgroup, self.dynamicgroup)

        for i in self.staticgroup.sprites():
            i.setgroup(self.planegroup)

    # 产生ignoreplaneid 和 attackignplaneid
    def firststep(self):
        planaction = {"VEL_x": 0, "VEL_y": 0, "ATTACK_TYPE": "RADAR", "ATTACK_ID": -100}
        for i in self.planegroup.sprites():
            if i.type is "JammerPlane":
                i.act(planaction, self.ignoreplaneid)
            elif i.type is "ThermalPlane":
                i.act(planaction, self.attackignplaneid)

    def step(self, side1_action, side2_action):
        self.attackignplaneid = []
        self.ignoreplaneid = []
        for i in self.planegroup.sprites():
            for j in side1_action:
                if j["ID"] == i.iid:
                    if i.type is "JammerPlane":
                        i.act(j, self.ignoreplaneid)
                    elif i.type is "ThermalPlane":
                        i.act(j, self.attackignplaneid)
                    else:
                        i.act(j)
        for i in self.staticgroup.sprites():
            i.act(self.attackignplaneid)
        for i in self.dynamicgroup.sprites():
            for j in side2_action:
                if j["ID"] == i.iid:
                    i.act(j)

        self.FPSCLOCK.tick(30)
        self.handle_event()
        self.DISPLAYSURE.fill((255, 255, 255))
        self.planegroup.update()
        self.planegroup.draw(self.DISPLAYSURE)
        self.staticgroup.update()
        self.staticgroup.draw(self.DISPLAYSURE)
        pygame.display.flip()

    def get_obs(self):
        side1_obs_raw = []
        side2_obs_raw = []
        for i in self.planegroup.sprites():
            side1_obs_raw.append(i.get_obs())

        for i in self.staticgroup.sprites():
            side2_obs_raw.append(i.get_obs(self.ignoreplaneid))

        for i in self.dynamicgroup.sprites():
            side2_obs_raw.append(i.get_obs(self.ignoreplaneid))

        return side1_obs_raw, side2_obs_raw

    def handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()


if __name__ == "__main__":
    env = ENVIROMENT(1080, 800, 1, 1, 1, 1, 1, 1, 1, 0)
    static = (env.staticgroup.sprites())[0]
    action = []
    planaction = {"ID": 2, "VEL_x": -1, "VEL_y": 1, "ATTACK_TYPE": "RADAR", "ATTACK_ID": -100}
    planaction2 = {"ID": 3, "VEL_x": -1, "VEL_y": 1, "ATTACK_TYPE": "RADAR", "ATTACK_ID": -100}
    action.append(planaction)
    action.append(planaction2)
    env.firststep()

    while True:
        env.FPSCLOCK.tick(30)
        k, j = env.get_obs()
        print(k)
        print(j)
        pos = k[2]["POS"]
        dx = round((static.x - pos[0]) / k[2]["VEL"])
        dy = round((static.y - pos[1]) / k[2]["VEL"])
        planaction["VEL_x"] = dx
        planaction["VEL_y"] = dy

        pos = k[3]["POS"]
        dx = round((static.x - pos[0]) / k[3]["VEL"])
        dy = round((static.y - pos[1]) / k[3]["VEL"])
        planaction2["VEL_x"] = dx
        planaction2["VEL_y"] = dy

        action = []
        print(planaction)
        action.append(planaction)
        action.append(planaction2)

        env.step(action, None)
