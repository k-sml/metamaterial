#この関数が合っているか様々な数値を入れて実験するためのファイルです(gds.pyのコピー)


import numpy as np
import math
import gdspy


def cal_tokakusseturitu(n, m, x, y):
    TE = x * n**2 + (1 - x) * m**2
    TM = y * n**(-2) + (1 - y) * m**(-2)

    ref = ((x * (1 / TM) + (1 - x) * m**2) / (y * (1 / TE) + (1 - y) * m**(-2)))**(1/4)
    return ref


def cal_isousa(r, f, λ):
    φ = -360*(np.sqrt(r**2 + f**2) - f)/λ
    return φ


def cal_isousa_occupancy(r, f, λ, H, silicon_ref):

    original_φ = -cal_isousa(r, f, λ)
    φ = -cal_isousa(r, f, λ)
    while φ > 360:
        φ -= 360
    Δn = (φ * λ / H) / 360
    Δn_360 = λ / H
    air_ref = 1.0
    # standard = (1.0 + silicon_ref) / 2   #基準
    standard = 1.8
    center_refrective = standard + Δn_360 / 2  #中心の等価屈折率
    r_refrective = center_refrective - Δn  #位置rでの等価屈折率
    x = np.arange(0.0, 1.0, 0.001)
    occupancy = 0
    for i in range(len(x)):
        if cal_tokakusseturitu(silicon_ref, air_ref, x[i], x[i]) > r_refrective:
            occupancy = x[i]
            break

    return original_φ, φ, Δn, center_refrective, r_refrective, occupancy 



def create_r_width(f, λ, H, silicon_ref, max_r, size, adjustment):
    lib = gdspy.GdsLibrary()
    cell = lib.new_cell('FIRST')
    y = np.arange(0.0, max_r, 400*10**(-9))
    r_occupancy = [0 for i in range(len(y))]
    for i in range(3, len(y)+3):
        original_φ, φ, Δn, center_refrective, r_refrective, occupancy = cal_isousa_occupancy(y[i-3], f, λ, H, silicon_ref)
        r_occupancy[i-3] = math.floor((1 - occupancy) * 100) / 100
    r_width = [0 for i in range(len(y)+3)]
    for i in range(len(y)):
        r_width[i] = math.floor(r_occupancy[i] * 200*10**(-6) * 10**(6))

    side_length = size - adjustment
    end = int(side_length / 200 / 2)

    for i in range(-end, end+1, 1):
        for j in range(-end, end+1, 1):
            x = i * 200
            y = j * 200
            z = math.floor(math.sqrt(x**2 + y**2)/200)
            # a = adjustment / 2 + end * 200
            # cell.add(gdspy.Rectangle((x - r_width[z]/2 +a, y + r_width[z]/2 +a), (x + r_width[z]/2 +a, y - r_width[z]/2 +a)))
            cell.add(gdspy.Rectangle((x + r_width[z]/2, y + r_width[z]/2), (x - r_width[z]/2, y - r_width[z]/2)))
    lib.write_gds('exp.gds')
    cell.write_svg('exp.gds')
    gdspy.LayoutViewer(lib)

create_r_width(1000*10**(-3), 532*10**(-9), 2.5*10**(-6), 1.46, 70.5*10**(-6), 100, 0)