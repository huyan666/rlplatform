import pygame
import random, pygame, sys, threading
from pygame.locals import *
import numpy as np
import math


class StaticThreaten(pygame.sprite.Sprite):

    def __init__(self, iid, x, y, hp, r):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("radar.png")
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.r = r
        self.hp = hp
        self.h = 0
        self.iid = iid
        self.lock = threading.Lock()
        self.color = (255, 255, 0, 180)
        self.screen = pygame.display.get_surface()
        self.rect.center = (self.x, self.y)
        self.env=None


    def update(self, surface):#*args
        self.lock.acquire(timeout=1)
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.r)#self.screen
        self.lock.release()

    def setgroup(self, planegroup):
        self.planegroup = planegroup

    def setenv(self,env):
        self.env=env

    def act(self, attackignplaneid, ignoreplaneid):
        return

    def get_score(self, target):
        score = 0
        if target.type is "RADAR":
            score = 100
        elif target.type in ["ADK", "AAG"]:
            score = 50
        elif target.type is "EnemyScoutPlane":
            score = 20
        elif target.type is "EnemyAttackPlane":
            score = 10
        elif target.type is "ScoutPlane":
            score = -100
        elif target.type is "AttackPlane":
            score = -50
        elif target.type in ["JammerPlane", "ThermalPlane"]:
            score = -30
        self.env.score += score


class RADAR(StaticThreaten):
    def __init__(self, iid, x, y, hp, r):
        super(RADAR, self).__init__(iid, x, y, hp, r)
        self.type = "RADAR"

    def get_obs(self, ignoreplaneid):
        radar_obs = {}
        radar_obs["ID"] = self.iid
        radar_obs["TYPE"] = self.type
        radar_obs["POS"] = [self.x, self.y, 0]
        target = []
        for i in self.planegroup.sprites():
            if i.h > self.r:
                continue
            if i.iid in ignoreplaneid:
                continue
            dis = ((self.x - i.x) ** 2 + (self.y - i.y) ** 2) ** 0.5
            if dis < self.r:
                plane_obs = {}
                plane_obs["ID"] = i.iid
                plane_obs["TYPE"] = i.type
                plane_obs["POS"] = [i.x, i.y, i.h]
                target.append(plane_obs)
        radar_obs["PLANE"] = target
        return radar_obs


class ADK(StaticThreaten):
    def __init__(self, iid, x, y, hp, r, hmax, hmin, dmax, dmin, damage):
        # __init__(self, iid, x, y, hp, r):
        super(ADK, self).__init__(iid, x, y, hp, r)
        self.hmax = hmax
        self.hmin = hmin
        self.dmax = dmax
        self.dmin = dmin
        self.damage = damage
        self.type = "ADK"
        self.r = dmax
        self.color = (255, 0, 0, 60)
        self.image = pygame.image.load("adk.png")
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def get_obs(self, ignoreplaneid):
        adk_obs = {}
        adk_obs["ID"] = self.iid
        adk_obs["TYPE"] = self.type
        adk_obs["POS"] = [self.x, self.y, 0]
        target = []
        for i in self.planegroup.sprites():
            if i.h > self.hmax:
                continue
            if i.iid in ignoreplaneid:
                continue
            dis = ((self.x - i.x) ** 2 + (self.y - i.y) ** 2) ** 0.5
            if dis < self.dmax:
                plane_obs = {}
                plane_obs["ID"] = i.iid
                plane_obs["TYPE"] = i.type
                plane_obs["POS"] = [i.x, i.y, i.h]
                target.append(plane_obs)
        adk_obs["PLANE"] = target
        return adk_obs

    def act(self, attackignplaneid, ignoreplaneid):
        for i in self.planegroup.sprites():
            if i.h > self.r:
                continue
            if i.iid in attackignplaneid or i.iid in ignoreplaneid:
                continue
            dis = ((self.x - i.x) ** 2 + (self.y - i.y) ** 2) ** 0.5
            if dis < self.dmax:
                '''
                damagerate = (self.dmax - dis) / (self.dmax - self.dmin)
                print(damagerate)
                if random.randint(0, 100) < (damagerate * 100):
                '''
                i.hp = i.hp - self.damage
                if i.hp < 0:
                    self.get_score(i)
                    i.kill()


class AAG(StaticThreaten):
    def __init__(self, iid, x, y, hp, r, hmax, dmax, damage):
        # __init__(self, iid, x, y, hp, r):
        super(AAG, self).__init__(iid, x, y, hp, r)
        self.hmax = hmax
        self.dmax = dmax
        self.damage = damage
        self.type = "AAG"
        self.r = dmax
        self.color = (255, 0, 0, 60)
        self.image = pygame.image.load("aag.png")
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self. y)

    def get_obs(self, ignoreplaneid):
        aag_obs = {}
        aag_obs["ID"] = self.iid
        aag_obs["TYPE"] = self.type
        aag_obs["POS"] = [self.x, self.y, 0]
        target = []
        for i in self.planegroup.sprites():
            if i.h > self.hmax:
                continue
            if i.iid in ignoreplaneid:
                continue
            dis = ((self.x - i.x) ** 2 + (self.y - i.y) ** 2) ** 0.5
            if dis < self.dmax:
                plane_obs = {}
                plane_obs["ID"] = i.iid
                plane_obs["TYPE"] = i.type
                plane_obs["POS"] = [i.x, i.y, i.h]
                target.append(plane_obs)
        aag_obs["PLANE"] = target
        return aag_obs

    def act(self, attackignplaneid, ignoreplaneid):
        for i in self.planegroup.sprites():
            if i.h > self.r:
                continue
            if i.iid in attackignplaneid or i.iid in ignoreplaneid:
                continue
            dis = ((self.x - i.x) ** 2 + (self.y - i.y) ** 2) ** 0.5
            if dis < self.dmax:
                '''
                damagerate = (self.dmax - dis) / (self.dmax - self.dmin)
                if random.randint(0, 100) < (damagerate * 100):
                '''
                i.hp = i.hp - self.damage
                if i.hp < 0:
                    self.get_score(i)
                    i.kill()
