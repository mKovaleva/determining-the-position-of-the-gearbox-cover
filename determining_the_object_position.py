from PIL import Image, ImageDraw, ImageFont
import math
import numpy as np

# функция для выделения предмета из красного фона, закрашивает предмет черным, а фон белым
def selection_background_and_center(image_path, result_path, result_format):
    # открываем картинку с помощью библиотеки
    im = Image.open(image_path)
    # считываем цвета всех пикселей в один массив 
    px = im.load()
    # считываем ширину и длину картинки по количеству пикселей
    width, height = im.size
    # заводим переменные для расчета центра крышки, n количество точек, summ_i и summ_j суммы координат по x и y
    n = 0
    summ_i = 0
    summ_j = 0
    # цикл по ширине и длине картинки по пикселям
    for i in range(width):
        for j in range(height):
            # получаем RGB одного пикселя 
            R,G,B = px[i, j]
            # условие для красного фона, если пиксель принадлежит фону, то меняется на белый, а если нет, то на черный
            if (2*G < R) & (2*B< R):
                im.putpixel((i, j), (255, 255, 255))
            else:
                im.putpixel((i, j), (0, 0, 0))
                # расчет для центра крышки
                summ_i+=i
                summ_j+=j
                n+=1
    # сохранение картинки, где деталь выделена черным, а фон белый
    im.save(result_path, result_format)
    # функция возвращает координаты центра предмета в пикселях
    return [int(summ_i/n), int(summ_j/n)]

# отрисовка центра детали
def center_drawing (image_path, coords, result_path, result_format):
    im = Image.open(image_path)
    for i_m in range(coords[0]-10, coords[0]+10):
        for j_m in range(coords[1]-10, coords[1]+10):
            im.putpixel((i_m, j_m), (255, 0, 0))

    # сохранение картинки с нарисованным центром детали
    im.save(result_path, result_format)

# закрашивание белого фона черным цветом
def painting_the_background_black (image_path, result_path, result_format):
    im = Image.open(image_path)
    px = im.load()
    width, height = im.size
    # перебор пикселей сверху-вниз, меняем белые пиксели на черные до первого черного пикселя
    for i in range(height):
        for j in range(width):
            current_color = px[j, i]
            if (current_color == (255, 255, 255)):
                im.putpixel((j, i), (0,0,0))
            else:
                break
    # перебор пикселей снизу-вверх, меняем белые пиксели на черные до первого черного пикселя                      
    for i in range(height-1, 0, -1):
        for j in range(width-1, 0, -1):
            current_color = px[j, i]
            if (current_color == (255, 255, 255)):
                im.putpixel((j, i), (0,0,0))
            else:
                break
    im_part1 = im
    
    im = Image.open(image_path)
    px = im.load()
    # перебор пикселей слева-направо, меняем белые пиксели на черные до первого черного пикселя
    for i in range(width):
        for j in range(height):
            current_color = px[i, j]
            if (current_color == (255, 255, 255)):
                im.putpixel((i, j), (0,0,0))
            else:
                break
    # перебор пикселей справа-налево, меняем белые пиксели на черные до первого черного пикселя
    for i in range(width-1, 0, -1):
        for j in range(height-1, 0, -1):
            current_color = px[i, j]
            if (current_color == (255, 255, 255)):
                im.putpixel((i, j), (0,0,0))
            else:
                break
    
    im_part2 = im
    # накладываем изображение с пикселями, закрашенными слева-направо и обратно, на изображение, с пикселями, закрашенными сверху вниз и обратно
    px_part1 = im_part1.load()
    px_part2 = im_part2.load()
    
    width, height = im_part1.size
    
    for i in range(height):
        for j in range(width):
            if (px_part1[j, i] != px_part2[j, i]):
                im_part1.putpixel((j, i), (0,0,0))
                
    # сохранение результата
    im_part1.save(result_path, result_format)
 
# устранение шума 
def elimination_of_noise (image_path, window_size, result_path, result_format):
    im = Image.open(image_path)
    px = im.load()
    width, height = im.size
    
    # создание эталонного окна черного и белого цветов
    reference_window_w = [[(255, 255, 255)] * window_size] * window_size
    reference_window_b = [[(0, 0, 0)] * window_size] * window_size
    
    # перемещение по картинке с шагом window_size
    for t in range(10):
        for i in range(0, width-(window_size+1), window_size+1):
            for j in range(0, height-(window_size+1), window_size+1):
                current_window = [[px[a,b] for a in range(i,i+window_size)] for b in range(j,j+window_size)]
                
                # если текущее окно не соответствует ни одному из двух эталонов, то закрашиваем его в черный
                if (current_window != reference_window_w) & (current_window != reference_window_b):
                    for i_p in range(i,i+window_size):
                        for j_p in range(j,j+window_size):
                            im.putpixel((i_p, j_p), (0,0,0))
    # сохраняем результат
    im.save(result_path, result_format)    

# нахождение центров отверстий
def find_centers_of_the_holes (image_path, window_size, result_path, result_format):
    im = Image.open(image_path)
    px = im.load()
    width, height = im.size
    # задаем эталонное окно размера window_size
    reference_window_w = [(255, 255, 255)] * window_size
    coord_arr = []
    for i in range(0, height):
        # перемещаемся построчно с шагом window_size
        for j in range(0, width-window_size):
            current_window = [px[a,i] for a in range(j+1,j+1+window_size)]
            summ_n = 0
            coord_number = 0
            # если текущее окно начинается с черного, а дальше идет эталонное белое окно, то закрашиваем его в красный и считаем среднее арифм. коорд.
            if (px[j, i] == (0,0,0)) & (current_window == reference_window_w):
                n = j+1
                while (px[n, i] == (255, 255, 255)):
                    im.putpixel((n, i), (255,0,0))
                    n+=1
                    summ_n+=n
                    coord_number+=1
                coord_center_x = summ_n/coord_number
                coord_arr.append([coord_center_x, i])
                im.putpixel((int(coord_center_x), i), (0,255,0))
    # получаем среднее арифметическое координат строк в отверстиях крышки           
    im.save(result_path, result_format)
    
    # расчет среднего арифметического от середин строк, получим центры отверстий
    summ_x = 0
    summ_y = 0
    n = 0
    hole_centers_arr = []
    for i in range(len(coord_arr)-1):
        if (coord_arr[i+1][1]-1) <= coord_arr[i][1]:
            summ_x+=coord_arr[i][0]
            summ_y+=coord_arr[i][1]
            n+=1
        else:
            if n != 0:
                hole_centers_arr.append((int(summ_x/n), int(summ_y/n)))
            summ_x = 0
            summ_y = 0
            n = 0
    hole_centers_arr.append((int(summ_x/n), int(summ_y/n)))
    
    return hole_centers_arr

# отрисовка центров отверстий
def hole_centers_drawing (image_path, coords, result_path, result_format):
    im = Image.open(image_path)
    for i in coords:
        for i_m in range(i[0]-10, i[0]+10):
            for j_m in range(i[1]-10, i[1]+10):
                    im.putpixel((i_m, j_m), (0, 0, 255))
    im.save(result_path, result_format)
    
def dotproduct(v1, v2):
        return sum((a*b) for a, b in zip(v1, v2))
    
def length(v):
    return math.sqrt(dotproduct(v, v))
    
# функция для расчета угла в радианах
def angle(v1, v2):
    return math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))

def midpoint (coords):
        return tuple(coords/2)

# расчет длин линий, соединяющих центры отверстий
def length_calculation (image_path, hole_centers, result_path, result_format):
    im = Image.open(image_path)
    width, height = im.size
    draw = ImageDraw.Draw(im) 
    font = ImageFont.truetype("OpenSans-Bold.ttf", 60)
    
    # отрисовка линий, которые соединяют центры отверстий
    draw.line((hole_centers[0], hole_centers[1]), fill=50, width=3)
    draw.line((hole_centers[1], hole_centers[2]), fill=50, width=3)
    draw.line((hole_centers[2], hole_centers[3]), fill=50, width=3)
    draw.line((hole_centers[3], hole_centers[4]), fill=50, width=3)
    draw.line((hole_centers[4], hole_centers[2]), fill=50, width=3)
    draw.line((hole_centers[2], hole_centers[0]), fill=50, width=3)
    draw.line((hole_centers[0], hole_centers[3]), fill=50, width=3)
    draw.line((hole_centers[1], hole_centers[4]), fill=50, width=3)
    
    # нумерация центров на картинке
    for i,j in enumerate(hole_centers):
         draw.text(j, str(i),font=font,)
    
    hole_centers_np_arr = np.array(hole_centers)
    
    a = round(length(hole_centers_np_arr[1] - hole_centers_np_arr[4]),2)
    b = round(length(hole_centers_np_arr[0] - hole_centers_np_arr[1]),2)
    c = round(length(hole_centers_np_arr[0] - hole_centers_np_arr[3]),2)
    d = round(length(hole_centers_np_arr[3] - hole_centers_np_arr[4]),2)
    
    l_arr =[a, b, c , d]
    
    l_max = max(l_arr)
    
    # вычисляем и отрисовываем отношения длин отрезков между центрами отверстий
    draw.text(midpoint(hole_centers_np_arr[1] + hole_centers_np_arr[4]), str(round(a/l_max, 2)),font=font,)
    draw.text(midpoint(hole_centers_np_arr[1] + hole_centers_np_arr[0]), str(round(b/l_max, 2)),font=font,)
    draw.text(midpoint(hole_centers_np_arr[0] + hole_centers_np_arr[3]), str(round(c/l_max, 2)),font=font,)
    draw.text(midpoint(hole_centers_np_arr[3] + hole_centers_np_arr[4]), str(round(d/l_max, 2)),font=font,)
      
    im.save(result_path, result_format)
    
    return [round(a/l_max, 2), round(b/l_max, 2), round(c/l_max, 2), round(d/l_max, 2)]
  
# расчет углов между отрезками, соединяющими центры отверстий и осью Х 
def angle_calculation (image_path, hole_centers, result_path, result_format):
    im = Image.open(image_path)
    draw = ImageDraw.Draw(im) 
    font = ImageFont.truetype("OpenSans-Bold.ttf", 60)
    
    # отрисовка линий, которые соединяют центры отверстий
    draw.line((hole_centers[0], hole_centers[1]), fill=50, width=3)
    draw.line((hole_centers[1], hole_centers[2]), fill=50, width=3)
    draw.line((hole_centers[2], hole_centers[3]), fill=50, width=3)
    draw.line((hole_centers[3], hole_centers[4]), fill=50, width=3)
    draw.line((hole_centers[4], hole_centers[2]), fill=50, width=3)
    draw.line((hole_centers[2], hole_centers[0]), fill=50, width=3)
    draw.line((hole_centers[0], hole_centers[3]), fill=50, width=3)
    draw.line((hole_centers[1], hole_centers[4]), fill=50, width=3)
    
    # нумерация центров на картинке
    for i,j in enumerate(hole_centers):
         draw.text(j, str(i),font=font,)
    
    hole_centers_np_arr = np.array(hole_centers)
    angle_arr = []
    
    # отмечаем на картинке угол наклона каждой линии (угол между линией и осью Х в градусах)
    # начало координат по оси х в левом нижнем углу, по оси у в левом верхем углу
    angle_arr.append(angle(hole_centers_np_arr[0] - hole_centers_np_arr[1], (1990, 0))* 180 / 3.14)
    angle_arr.append(angle(hole_centers_np_arr[1] - hole_centers_np_arr[2], (1990, 0))* 180 / 3.14)
    angle_arr.append(angle(hole_centers_np_arr[2] - hole_centers_np_arr[3], (1990, 0))* 180 / 3.14)
    angle_arr.append(angle(hole_centers_np_arr[3] - hole_centers_np_arr[4], (1990, 0))* 180 / 3.14)
    angle_arr.append(angle(hole_centers_np_arr[2] - hole_centers_np_arr[4], (1990, 0))* 180 / 3.14)
    angle_arr.append(angle(hole_centers_np_arr[0] - hole_centers_np_arr[2], (1990, 0))* 180 / 3.14)
    angle_arr.append(angle(hole_centers_np_arr[0] - hole_centers_np_arr[3], (1990, 0))* 180 / 3.14)
    angle_arr.append(angle(hole_centers_np_arr[1] - hole_centers_np_arr[4], (1990, 0))* 180 / 3.14)
    
    
    draw.text(midpoint(hole_centers_np_arr[1] + hole_centers_np_arr[0]), str(round(angle_arr[0]))+"°",font=font,)
    draw.text(midpoint(hole_centers_np_arr[2] + hole_centers_np_arr[1]), str(round(angle_arr[1]))+"°",font=font,)
    draw.text(midpoint(hole_centers_np_arr[2] + hole_centers_np_arr[3]), str(round(angle_arr[2]))+"°",font=font,)
    draw.text(midpoint(hole_centers_np_arr[3] + hole_centers_np_arr[4]), str(round(angle_arr[3]))+"°",font=font,)
    draw.text(midpoint(hole_centers_np_arr[2] + hole_centers_np_arr[4]), str(round(angle_arr[4]))+"°",font=font,)
    draw.text(midpoint(hole_centers_np_arr[0] + hole_centers_np_arr[2]), str(round(angle_arr[5]))+"°",font=font,)
    draw.text(midpoint(hole_centers_np_arr[0] + hole_centers_np_arr[3]), str(round(angle_arr[6]))+"°",font=font,)
    draw.text(midpoint(hole_centers_np_arr[1] + hole_centers_np_arr[4]), str(round(angle_arr[7]))+"°",font=font,)
      
    im.save(result_path, result_format)
    
# определение положения крышки, итоговая функция
def determine_the_position (image_path):
    centr_coords = selection_background_and_center(image_path, image_path[:-4]+"_res1.bmp", "BMP")    
    center_drawing(image_path[:-4]+"_res1.bmp", centr_coords, image_path[:-4]+"_res2.bmp", "BMP")
    
    painting_the_background_black (image_path[:-4]+"_res1.bmp", image_path[:-4]+"_res3.bmp", "BMP")
    
    finding_blue_light(image_path, image_path[:-4]+"_res4.bmp", "BMP")
    
    elimination_of_noise (image_path[:-4]+"_res3.bmp", 17, image_path[:-4]+"_res5.bmp", "BMP")
    
    hole_centers = find_centers_of_the_holes (image_path[:-4]+"_res5.bmp", 32, image_path[:-4]+"_res6.bmp", "BMP")
    
    # координаты центров отверстий в пикселях
    print("координаты центров отверстий в пикселях " + str(hole_centers))
    
    hole_centers_drawing (image_path[:-4]+"_res1.bmp", hole_centers, image_path[:-4]+"_res8.bmp", "BMP")
    hole_centers_drawing (image_path, hole_centers, image_path[:-4]+"_res9.bmp", "BMP")
    angle_calculation (image_path[:-4]+"_res9.bmp", hole_centers, image_path[:-4]+"_res10.bmp", "BMP")
    result = length_calculation (image_path[:-4]+"_res9.bmp", hole_centers, image_path[:-4]+"_res11.bmp", "BMP")
    result = np.array(result)
    
    # отношения длин сторон
    print ("отношения длин сторон " + str(result))
    
    
determine_the_position("img_red_background.jpg") 
determine_the_position("img1_red_background.jpg") 