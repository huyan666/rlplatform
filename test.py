from enviroment import *
from AgentPlan import *



if __name__ == "__main__":
    env = ENVIROMENT(500, 500, 1, 1, 1, 1, 1, 1, 1, 1, 1)
    env.firststep()
    side1=AgentPlan(500,500)
    while True:
        env.FPSCLOCK.tick(30)
        k, j = env.get_obs()
        side1.construct_common_obs(k)
        action1=side1.get_action()
        env.step(action1, None)