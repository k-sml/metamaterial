from PIL import Image, ImageDraw
import numpy as np
import math


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
    # print('中心との位相差は' + str(φ) + '°')
    while φ > 360:
        φ -= 360
    # print('360°調整した位相差は' + str(φ))
    Δn = (φ * λ / H) / 360
    # print('中心との屈折率差は' + str(Δn))
    Δn_360 = λ / H
    air_ref = 1.0
    # standard = (1.0 + silicon_ref) / 2   #基準
    # standard = 1.8
    standard = 1.5   #7.5用
    center_refrective = standard + Δn_360 / 2  #中心の等価屈折率
    r_refrective = center_refrective - Δn  #位置rでの等価屈折率
    # print('中心の等価屈折率は' + str(center_refrective))
    # print('位置rの等価屈折率は' + str(r_refrective))
    x = np.arange(0.0, 1.0, 0.001)
    occupancy = 0
    for i in range(len(x)):
        if cal_tokakusseturitu(silicon_ref, air_ref, x[i], x[i]) > r_refrective:
            occupancy = x[i]
            break
    # print('位置rの占有率は' + str(occupancy))

    return original_φ, φ, Δn, center_refrective, r_refrective, occupancy 



def create_r_width(f, λ, H, silicon_ref, max_r, size, adjustment):
    y = np.arange(0.0, max_r, 0.2*10**(-3))
    # print(len(y))
    r_occupancy = [0 for i in range(len(y))]
    for i in range(3, len(y)+3):
        original_φ, φ, Δn, center_refrective, r_refrective, occupancy = cal_isousa_occupancy(y[i-3], f, λ, H, silicon_ref)
        # occupancy = math.floor(occupancy*100) / 100
        r_occupancy[i-3] = math.floor((1 - occupancy) * 100) / 100
    # print(r_occupancy)
    r_width = [0 for i in range(len(y)+3)]
    # print(len(r_occupancy))
    for i in range(len(y)):
        r_width[i] = math.floor(r_occupancy[i] * 200*10**(-6) * 10**(6))
    # print(len(r_width))
    im = Image.new('RGB', (size, size), (0, 192, 192))
    draw = ImageDraw.Draw(im)
    side_length = size - adjustment
    end = int(side_length / 200 / 2)

    for i in range(-end, end+1, 1):
        for j in range(-end, end+1, 1):
            x = i * 200
            y = j * 200
            z = math.floor(math.sqrt(x**2 + y**2)/200)
            a = adjustment / 2 + end * 200
            # draw.rectangle((200*i-100+17500, 200*j+100+17500, 200*i+100+17500, 200*j-100+17500), fill=(0, 192, 192), outline=(255, 255, 255))
            draw.rectangle((x - r_width[z]/2 +a, y + r_width[z]/2 +a, x + r_width[z]/2 +a, y - r_width[z]/2 +a), fill=(256, 256, 256), outline=None)
    
    im.save('pillowdraw.jpg')
    im.show()

        
create_r_width(100*10**(-3), 750*10**(-6), 500*10**(-6), 3.4, 11*10**(-3), 20000, 4000)
# create_r_width(100*10**(-3), 750*10**(-6), 500*10**(-6), 3.4, 21.15*10**(-3), 35000, 5000)


# im = Image.new('RGB', (500, 500), (128, 128, 128))
# draw = ImageDraw.Draw(im)

# for i in range(-2, 3, 1):
#     for j in range(-2, 3, 1):
#         draw.rectangle((20*i-5+50, 20*j+5+50, 20*i+5+50, 20*j-5+50), fill=(0, 192, 192), outline=(255, 255, 255))

# im.save('pillowdraw.jpg')
# im.show()