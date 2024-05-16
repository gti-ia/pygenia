import math


def f(x, k, c, a):
    return 1 / (a + math.exp(k * (x + c)))


def estimate_next_offer(mood, others_emotion, empathic_level, affective_link):
    # k y c deben ser [0,2]
    offer = f(
        others_emotion,
        5,
        -affective_link,
        5 - (affective_link + (1 + mood)) * empathic_level,
    )
    print(
        "---__",
        5 - (affective_link + (1 + mood)) * empathic_level,
    )
    return (offer, 1 - offer)


mood = 1
others_emotion = -0.2
empathic_level = 1
affective_link = 0.1
print(estimate_next_offer(mood, others_emotion, empathic_level, affective_link))
