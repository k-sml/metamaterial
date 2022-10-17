#パラメータを入力すると、それに基づいてgds2ファイルが生成されます


import numpy as np
import math
import gdspy


#(n, m)は媒質の屈折率、x, yはx方向、y方向の占有率
def cal_tokakusseturitu(n, m, x, y):
    TE = x * n**2 + (1 - x) * m**2
    TM = y * n**(-2) + (1 - y) * m**(-2)

    ref = ((x * (1 / TM) + (1 - x) * m**2) / (y * (1 / TE) + (1 - y) * m**(-2)))**(1/4)
    return ref



#位置r, 焦点距離f, 波長λの位相差を計算
def cal_isousa(r, f, λ):
    φ = -360*(np.sqrt(r**2 + f**2) - f)/λ
    return φ



#位置r, 焦点距離f, 波長λ, 高さH, シリコンの屈折率silicon_refからその場所のあるべき占有率などの情報を計算
def cal_isousa_occupancy(r, f, λ, H, silicon_ref):

    original_φ = -cal_isousa(r, f, λ)
    φ = -cal_isousa(r, f, λ)   #中心との位相差
    while φ > 360:
        φ -= 360   #360°調整した中心との位相差
    Δn = (φ * λ / H) / 360   #中心との屈折率差
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
            occupancy = x[i]   #位置rでの占有率
            break

    return original_φ, φ, Δn, center_refrective, r_refrective, occupancy 



#占有率からwidthを算出、gds2ファイルで設計する
#焦点距離f, 波長λ, 高さH, シリコンの屈折率silicon_ref, 中心からの最大長さmax_r, 設計するウエハの一辺の長さsize, ウエハの中で加工する部分とsizeとの差
def create_r_width(f, λ, H, silicon_ref, max_r, size, adjustment):
    lib = gdspy.GdsLibrary()
    cell = lib.new_cell('FIRST')
    y = np.arange(0.0, max_r, 0.2*10**(-3))
    r_occupancy = [0 for i in range(len(y))]
    for i in range(3, len(y)+3):
        original_φ, φ, Δn, center_refrective, r_refrective, occupancy = cal_isousa_occupancy(y[i-3], f, λ, H, silicon_ref)
        # occupancy = math.floor(occupancy*100) / 100
        r_occupancy[i-3] = math.floor((1 - occupancy) * 10000) / 10000
    r_width = [0 for i in range(len(y)+3)]
    for i in range(len(y)):
        r_width[i] = math.floor(r_occupancy[i] * 200*10**(-6) * 10**(8)) / 100
    print(r_width)
    side_length = size - adjustment
    end = int(side_length / 200 / 2)

    for i in range(-end, end+1, 1):
        for j in range(-end, end+1, 1):
            x = i * 200
            y = j * 200
            z = math.floor(math.sqrt(x**2 + y**2)/200)
            cell.add(gdspy.Rectangle((x + r_width[z]/2, y + r_width[z]/2), (x - r_width[z]/2, y - r_width[z]/2)))
    lib.write_gds('make_gds.gds')
    cell.write_svg('make_gds.svg')
    gdspy.LayoutViewer(lib)

create_r_width(100*10**(-3), 750*10**(-6), 500*10**(-6), 3.4, 21.15*10**(-3), 35000, 5000)