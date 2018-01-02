import random


def get_random_reward():
    """
    Get random reward
    :return: return random reward

    """
    pass
    rewards = [0.2, 0.1, 0.05, 0.04, 0.03, 0.02, 0.01]
    return random.choice(rewards)


def run_as_standalone():
    reward = get_random_reward()
    print(reward)


if __name__ == "__main__":
    run_as_standalone()
