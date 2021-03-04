import math


def kelly_criterion(probability: float):
    edge = 0
    if probability <= 1.5:
        edge = 1
    payout_factor = round(probability - 1, 2)
    percentage_win = math.ceil(1 / probability * 100) + edge
    percentage_loss = 100 - percentage_win
    win_factor = percentage_win / 100
    loss_factor = percentage_loss / 100
    return round((payout_factor * win_factor - loss_factor) / payout_factor, 3)
