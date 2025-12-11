import math

def pdf(x) :
    """标准正态分布 PDF"""
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)

def cdf(x) :
    """标准正态分布 CDF"""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def v_func(t):
    """均值更新函数 (无平局)"""
    denom = cdf(t)
    if denom < 1e-10:  # 数值保护：极端爆冷情况
        return -t
    return pdf(t) / denom

def w_func(t):
    """方差更新函数 (无平局)"""
    v = v_func(t)
    return v * (v + t)


class Rating:
    def __init__(self, mean=25.0, std=8.33):
        self.mean = mean
        self.var = std ** 2

    @property
    def std(self):
        return math.sqrt(self.var)

    @classmethod
    def from_var(cls, mean, var):
        r = cls.__new__(cls)
        r.mean = mean
        r.var = var
        return r


beta = 4.17
tau_sq = 0.1


def match1v1(winner : Rating, loser : Rating):
    w_var = winner.var + tau_sq
    l_var = loser.var + tau_sq

    c_sq = 2 * beta**2 + w_var + l_var
    c = math.sqrt(c_sq)
    t = (winner.mean - loser.mean) / c


    winner_update_mean = winner.mean + w_var / c * v_func(t)
    winner_update_var = w_var  * (1 - w_var / c_sq * w_func(t))

    loser_update_mean = loser.mean - l_var / c * v_func(t)
    loser_update_var = l_var  * (1 - l_var / c_sq * w_func(t))

    winnerUpdate = Rating.from_var(winner_update_mean, winner_update_var)
    loserUpdate = Rating.from_var(loser_update_mean, loser_update_var)

    return winnerUpdate,loserUpdate