import random, pygame, sys, threading
from pygame.locals import *
import numpy as np
import math

from PLANESPRITE import *
from STATICTHREATEN import *


class ENVIROMENT:

    def __init__(self, x, y, attacknums, scoutnums, jammernums, thermalnums, radarnums, adknums, aagnums,
                 enemyattacknums, enemyscoutnums):
        self.mapsize_x = x
        self.mapsize_y = y

        self.attacknums = attacknums
        self.scoutnums = scoutnums
        self.jammernums = jammernums
        self.thermalnums = thermalnums

        self.radarnums = radarnums
        self.adknums = adknums
        self.aagnums = aagnums

        self.enemyattacknums = enemyattacknums
        self.enemyscoutnums = enemyscoutnums

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
            x = random.randint(0, self.mapsize_x/2)
            y = random.randint(0, self.mapsize_y)
            a = AttackPlane(planeid, x, y, 10, 20, 5, 100, 0.8)
            planeid += 1
            self.planegroup.add(a)

        for i in range(self.scoutnums):
            x = random.randint(0, self.mapsize_x/2)
            y = random.randint(0, self.mapsize_y)
            a = ScoutPlane(planeid, x, y, 10, 100, 5)
            planeid += 1
            self.planegroup.add(a)

        for i in range(self.jammernums):
            x = random.randint(0, self.mapsize_x/2)
            y = random.randint(0, self.mapsize_y)
            a = JammerPlane(planeid, x, y, 10, 20, 5)
            planeid += 1
            self.planegroup.add(a)

        for i in range(self.attacknums):
            x = random.randint(0, self.mapsize_x/2)
            y = random.randint(0, self.mapsize_y)
            a = ThermalPlane(planeid, x, y, 10, 20, 5)
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

        dynamicid = 0
        for i in range(self.enemyattacknums):
            x = random.randint(self.mapsize_x/2, self.mapsize_x)
            y = random.randint(0, self.mapsize_y)
            a = EnemyAttackPlane(dynamicid, x, y, 10, 20, 10, 100, 0.8)
            dynamicid += 1
            self.dynamicgroup.add(a)

        for i in range(self.enemyscoutnums):
            x = random.randint(self.mapsize_x/2, self.mapsize_x)
            y = random.randint(0, self.mapsize_y)
            a = EnemyScoutPlane(dynamicid, x, y, 10, 20, 10)
            dynamicid += 1
            self.dynamicgroup.add(a)

        for i in self.planegroup.sprites():
            i.setgroup(self.planegroup, self.staticgroup, self.dynamicgroup)

        for i in self.staticgroup.sprites():
            i.setgroup(self.planegroup)

        for i in self.dynamicgroup.sprites():
            i.setgroup(self.planegroup, self.staticgroup, self.dynamicgroup)

    # 产生ignoreplaneid 和 attackignplaneid
    def firststep(self):
        planaction = {"DIRECTION": 90, "ATTACK_TYPE": "RADAR", "ATTACK_ID": -100}
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
            i.act(self.attackignplaneid, self.ignoreplaneid)
        for i in self.dynamicgroup.sprites():
            if side2_action is None:
                continue
            for j in side2_action:
                if j["ID"] == i.iid:
                    i.act(j, self.ignoreplaneid, self.attackignplaneid)

        self.FPSCLOCK.tick(30)
        self.handle_event()
        self.DISPLAYSURE.fill((255, 255, 255))

        self.planegroup.update()
        self.planegroup.draw(self.DISPLAYSURE)

        self.staticgroup.update()
        self.staticgroup.draw(self.DISPLAYSURE)

        self.dynamicgroup.update()
        self.dynamicgroup.draw(self.DISPLAYSURE)
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


def get_angel(x1, y1, x2, y2):
    return math.atan2(y2 - y1, x2 - x1)

'''
if __name__ == "__main__":
    env = ENVIROMENT(800, 800, 1, 1, 1, 1, 1, 1, 1, 1, 1)
    static = (env.staticgroup.sprites())[0]
    action = []
    planaction = {"ID": 2, "DIRECTION": math.radians(0), "ATTACK_TYPE": "RADAR", "ATTACK_ID": -100}
    planaction2 = {"ID": 3, "DIRECTION": math.radians(0), "ATTACK_TYPE": "RADAR", "ATTACK_ID": -100}
    action.append(planaction)
    action.append(planaction2)
    env.firststep()

    while True:
        env.FPSCLOCK.tick(30)
        k, j = env.get_obs()
        print(k)
        pos = k[2]["POS"]
        print(k[2])
        planaction["DIRECTION"] = math.atan2(static.y - pos[1], static.x - pos[0])
        print(planaction)

        pos = k[3]["POS"]

        planaction2["DIRECTION"] = math.atan2(static.y - pos[1], static.x - pos[0])
        print("angel")
        print(math.degrees(planaction2["DIRECTION"]))
        print(planaction2)

        action = []
        action.append(planaction)
        action.append(planaction2)

        env.step(action, None)
'''