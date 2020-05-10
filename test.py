from enviroment import *
from AgentPlan import *
from EnemyPlan import *

if __name__ == "__main__":
    env = ENVIROMENT(500, 500, 2, 1, 1, 1, 1, 1, 1, 1, 1)
    env.firststep()
    side1 = AgentPlan(500, 500)
    side2 = EnemyPlan(500, 500)
    while True:
        env.FPSCLOCK.tick(30)
        k, j = env.get_obs()
        side1.construct_common_obs(k)
        side2.construct_common_obs(j)

        action1 = side1.get_action()
        action2 = side2.get_action()
        env.step(action1, action2)
        flag = env.get_done()
        if flag == 1:
            print("YOU LOSE")
            break
        elif flag == 2:
            print("YOU WIN")
