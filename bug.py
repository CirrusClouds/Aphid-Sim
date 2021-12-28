from typing import Dict, TypedDict, List, Tuple, Union
import random
import math

import numpy as np
import matplotlib.pyplot as plt

# Bugs' ability to survive will be determined by 3 factors. Their resistance to heat, their speed, and their camoflage. Bugs eat Aphids.

# Aphids don't need to consume but live much shorter lives than bugs. They reproduce faster.

# As aphids grow, they are contained by the space they're in

# As bugs grow, the prey supply dwindles

# Environment becomes hotter over time and bugs need to adapt

# Natural selection at work!

# Object definitions


class Creature():
    age: int = 0

    def __init__(self, speed: int):
        self.id = random.randint(0, 999999)
        self.age: int = 0
        self.speed = speed


class Bug(Creature):

    def __init__(self, heat_resistance: int, speed: int, camoflage: int):
        super().__init__(speed)
        self.heat_resistance = heat_resistance
        self.camoflage = camoflage

    def reproduce(self, environment: TypedDict):
        childspeed = self.speed + random.randint(-2, 2)
        childheatresist = self.heat_resistance + random.randint(-2, 2)
        childcamoflage = self.camoflage + random.randint(-2, 2)

        if random.randint(0, 100) > 75:  # chance to reproduce more than once
            environment["bugs"].append(Bug(heat_resistance=childheatresist,
                                           speed=childspeed,
                                           camoflage=childcamoflage))

        # chance to reproduce more than once
        if random.randint(0, 100) > 90:
            environment["bugs"].append(Bug(heat_resistance=childheatresist,
                                           speed=childspeed,
                                           camoflage=childcamoflage))

        if len(environment["aphids"]) > 0.9*(environment["aphid_space"]):
            environment["bugs"].append(Bug(heat_resistance=childheatresist,
                                           speed=childspeed,
                                           camoflage=childcamoflage))

        # print("The bug reproduces!")

    def survival_test(self, environment: TypedDict) -> Tuple[bool, str]:
        if bug.heat_resistance < environment["heat"]:
            return (False, "heat_resistance")

        return (True, "")

    def hunt(self, environment: TypedDict) -> bool:
        potential_prey: List[Aphid] = list(filter(lambda aphid: (aphid.speed < self.speed) and (
            aphid.awareness < self.camoflage), environment["aphids"]))

        if len(potential_prey) > 0:
            num_to_eat = math.ceil(len(potential_prey) / (len(environment["bugs"])*1.2) + (
                0.8 if len(environment["aphids"]) > 1.5*len(environment["bugs"]) else 0.4))
            preys = potential_prey[0:num_to_eat]
            for prey in preys:
                delete_creature(prey.id, "aphids", environment)

            return True
        else:
            # print("The bug starved!")
            return False


class Aphid(Creature):
    def __init__(self, awareness: int, speed: int):
        super().__init__(speed)
        self.awareness = awareness

    def reproduce(self, environment: TypedDict):
        childspeed = self.speed + random.randint(-2, 2)
        childawareness = self.awareness + random.randint(-2, 2)

        e_s_ratio: float = len(environment["aphids"])/environment["aphid_space"]

        if e_s_ratio > 1:
            if random.random() < e_s_ratio - 1:
                delete_creature(self.id, "aphids", environment)
                return False

        if random.randint(0, 100) > 67:
            environment["aphids"].append(Aphid(speed=childspeed,
                                               awareness=childawareness))

        if random.randint(0, 100) > 90:
            environment["aphids"].append(Aphid(speed=childspeed,
                                               awareness=childawareness))


class Environment(TypedDict):
    bugs: List[Bug]
    aphids: List[Aphid]
    heat: int
    prey_speed: int
    prey_awareness: int
    aphid_space: int

# Functions


def make_random_critters(n: int, critter: str) -> List[Union[Bug, Aphid]]:
    creatures: Union[List[Bug], List[Aphid]] = []

    for i in range(n):
        if critter == "bugs":
            creatures.append(Bug(heat_resistance=random.randint(0, 16),
                                 speed=random.randint(0, 16),
                                 camoflage=random.randint(0, 16)))
        if critter == "aphids":
            creatures.append(Aphid(speed=random.randint(0, 9),
                                   awareness=random.randint(0, 9)))

    return creatures


def delete_creature(id: int, critter: str, environment: TypedDict):
    environment[critter] = list(filter(lambda creature: creature.id != id, environment[critter]))


# Main loop

if __name__ == "__main__":
    environment = {
        "bugs": make_random_critters(100, "bugs"),
        "aphids": make_random_critters(500, "aphids"),
        "heat": 9,
        "aphid_space": 2000,
    }

    MAX_TIME = 100

    time_array = np.arange(0, MAX_TIME, step=1)
    aphid_array = np.zeros(MAX_TIME)
    bug_array = np.zeros(MAX_TIME)

    i = 0
    while(i < MAX_TIME):
        aphid_array[i] = len(environment["aphids"])
        bug_array[i] = len(environment["bugs"])

        if i % 5 == 0:
            environment["heat"] += 1

        print(f"Round {i}")
        print(f"There are {len(environment['bugs'])} bugs")
        print(f"There are {len(environment['aphids'])} aphids")
        for bug in environment["bugs"]:
            if bug.age >= 10:  # creatures die when they get too old
                delete_creature(bug.id, "bugs", environment)
                continue

            survival_test_results = bug.survival_test(environment)
            if survival_test_results[0]:
                # Bug dies permanently if it can't consume because there are too many bugs
                consumes: bool = bug.hunt(environment)

                if consumes:
                    bug.reproduce(environment)
                    bug.age += 1
                else:
                    delete_creature(bug.id, "bugs", environment)

            else:
                reason: str = survival_test_results[1]
                # print(f"death due to insufficient {reason}, try again mr. bug")
                delete_creature(bug.id, "bugs", environment)

        for aphid in environment["aphids"]:
            if aphid.age >= 5:
                delete_creature(aphid.id, "aphids", environment)
                continue

            aphid.reproduce(environment)
            aphid.age += 1

        i += 1
        print("\n")

    # Plot

    plt.figure()
    plt.grid()
    plt.title("Population of ants vs. aphids")
    plt.xlabel("Rounds")
    plt.ylabel("Population")
    plt.plot(time_array, aphid_array, label="Aphids")
    plt.plot(time_array, bug_array, label="Bugs")
    plt.legend()
    plt.show()
