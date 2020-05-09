from enviroment import *
import copy


class AgentPlan:
    def __init__(self, mapsizex, mapsizey):
        self.mapsizex = mapsizex
        self.mapsizey = mapsizey
        self.side_obs_raw = None
        self.common_obs = []
        self.plane = []

    def construct_common_obs(self, side_obs_row):
        self.side_obs_raw = copy.deepcopy(side_obs_row)
        for i in self.side_obs_raw:
            if len(i["THREAT"]) != 0:
                for j in i["THREAT"]:
                    id = [x["ID"] for x in self.common_obs]
                    if j["ID"] in id:
                        for x in self.common_obs:
                            if x["ID"] == j["ID"]:
                                x["POS"] = copy.deepcopy(j["POS"])
                    else:
                        self.common_obs.append(j)

    def get_action(self):
        action = []
        print(self.common_obs)
        for i in self.side_obs_raw:
            plan_action = {}
            plan_action["ID"] = i["ID"]
            pos = i["POS"]
            if len(i["THREAT"]) == 0:
                if len(self.common_obs) == 0:
                    plan_action["DIRECTION"] =self.get_direction(pos[0],pos[1],i["DIRECTION"])
                    print(plan_action)

                    if i["TYPE"] is "AttackPlane":
                        plan_action["ATTACK_TYPE"] = "RADAR"
                        plan_action["ATTACK_ID"] = -100
                else:
                    targetx, targety, targetid, target_type = self.get_closed_threat(pos[0], pos[1])

                    plan_action["DIRECTION"] = self.get_angel(pos[0], pos[1], targetx, targety)
                    if i["TYPE"] is "AttackPlane":
                        plan_action["ATTACK_TYPE"] = "RADAR"
                        plan_action["ATTACK_ID"] = -100
            else:
                targetx = i["THREAT"][0]["POS"][0]
                targety = i["THREAT"][0]["POS"][1]
                angel = self.get_angel(pos[0], pos[1], targetx, targety)
                plan_action["DIRECTION"] = angel
                if i["TYPE"] is "AttackPlane":
                    plan_action["ATTACK_TYPE"] = i["THREAT"][0]["TYPE"]
                    plan_action["ATTACK_ID"] = i["THREAT"][0]["ID"]
                    for k in self.common_obs:
                        if k["ID"] == i["THREAT"][0]["ID"]:
                            self.common_obs.remove(k)
            action.append(copy.deepcopy(plan_action))
        return action

    def get_angel(self, x, y, targetx, targety):
        return math.atan2(targety - y, targetx - x)

    def get_direction(self,x,y,direction):
        if x>self.mapsizex:
            if y>self.mapsizey:
                direction=math.radians(225)
            else:
                direction=math.radians(135)
        elif x<0:
            if y>self.mapsizey:
                direction=math.radians(-45)
            else:
                direction=math.radians(45)
        else:
            if y>self.mapsizey:
                direction=math.radians(-45)
            elif y<0:
                direction=math.radians(45)
            else:
               pass
        return direction
    def get_closed_threat(self, x, y):
        dismin = 10000
        target_type = None
        target_id = None
        target_x = 0
        target_y = 0
        for i in self.common_obs:
            dis = ((x - i["POS"][0]) ** 2 + (y - i["POS"][1]) ** 2) ** 0.5
            if (dismin > dis):
                dismin = dis
                target_id = i["ID"]
                target_type = i["TYPE"]
                target_x = i["POS"][0]
                target_y = i["POS"][1]
        return target_x, target_y, target_id, target_type


'''
    [{'ID': 0, 'TYPE': 'AttackPlane', 'POS': [269, 334, 10], 'VEL': 10, 'RADIUS': 20, 'DAMAGE': 100, 'DAMAGERATE': 0.8,
      'THREAT': []}, 
     {'ID': 1, 'TYPE': 'ScoutPlane', 'POS': [381, 258, 10], 'VEL': 10, 'RADIUS': 20, 'THREAT': []},
     {'ID': 2, 'TYPE': 'JammerPlane', 'POS': [736.9742079326046, 13.735631207394697, 10], 'VEL': 10, 'RADIUS': 20,
      'THREAT': [{'ID': 0, 'TYPE': 'RADAR', 'POS': [756, 13, 0], 'RADIUS': 100}]},
     {'ID': 3, 'TYPE': 'ThermalPlane', 'POS': [754.1292095327325, 13.66351959959929, 10], 'VEL': 10, 'RADIUS': 20,
      'THREAT': [{'ID': 0, 'TYPE': 'RADAR', 'POS': [756, 13, 0], 'RADIUS': 100}]}]
'''
