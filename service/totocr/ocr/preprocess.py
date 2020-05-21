import numpy as np
import cv2


def preprocess_enaval_form(img,DEBUG=False):

    # Convert to grayscale
    if(img.shape[2] == 3):
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img
    gray = 255 - gray
    if DEBUG:
        show_wait_destroy(gray,"gray",scale=0.3)
    height, width = gray.shape[:2]

    # Binariza e remove pequenos ruídos
    bw = cv2.threshold(gray, 70, 255, cv2.THRESH_OTSU  )[1] # cv2.THRESH_OTSU cv2.THRESH_BINARY
    if DEBUG:
        show_wait_destroy(bw,"bw",scale=0.3)
    morph_struct = cv2.getStructuringElement(cv2.MORPH_RECT , (5,5))
    morph_img = cv2.morphologyEx(bw,cv2.MORPH_CLOSE,morph_struct)
    # morph_img = cv2.morphologyEx(morph_img,cv2.MORPH_OPEN,morph_struct)
    if DEBUG:
        show_wait_destroy(morph_img,"morph out",scale=0.3)
    
    # Define kernel para ressaltar linha. (baseado na Laplacian of Gaussian)
    line_size = int(width * 9/2480) # espessura da linha em pixels
    kernel_size_x = line_size*5
    kernel_size_y = line_size*5
    kernel_sigma = line_size/2
    kernel_mu = kernel_size_x/2
    kernel = np.zeros((kernel_size_y,kernel_size_x))
    for x in np.arange(kernel_size_x):
        for y in np.arange(kernel_size_y):
            kernel[y,x]=-np.exp(-(x-kernel_mu)**2/(2*kernel_sigma**2)) * ((x-kernel_mu)**2-kernel_sigma**2) / (kernel_sigma**4)
    if DEBUG:
        show_wait_destroy(kernel, "filter kernel", normalize=True)

    
    # Filtra a imagem para ressaltar linhas horizontais e verticais
    img_filt_vert = cv2.filter2D(morph_img,cv2.CV_32F,kernel)
    img_filt_vert = cv2.threshold(img_filt_vert,0,0,cv2.THRESH_TOZERO)[1] # valores negativos não interessam
    img_filt_vert = cv2.normalize(img_filt_vert,  img_filt_vert, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    img_filt_vert = cv2.threshold(img_filt_vert,60,255,cv2.THRESH_BINARY)[1]

    img_filt_horiz = cv2.filter2D(morph_img,cv2.CV_32F,cv2.rotate(kernel,cv2.ROTATE_90_CLOCKWISE))
    img_filt_horiz = cv2.threshold(img_filt_horiz,0,0,cv2.THRESH_TOZERO)[1]
    img_filt_horiz = cv2.normalize(img_filt_horiz,  img_filt_horiz, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    img_filt_horiz = cv2.threshold(img_filt_horiz,60,255,cv2.THRESH_BINARY)[1]
    if DEBUG:
        show_wait_destroy(img_filt_vert,"filtered vertical",scale=0.3,normalize=True)
        show_wait_destroy(img_filt_horiz,"filtered horizontal",scale=0.3,normalize=True)

    # Acha linhas esquerda e direita
    thrs=int(height*0.5) # a linha deve ter ao menos 1/2 do tamanho vertical
    found_vert_lines = False
    while not found_vert_lines:
        lines_vert = cv2.HoughLines(img_filt_vert, 1, np.pi / 720, thrs)
        if lines_vert is None:
            thrs = int(thrs*0.9)
            continue
        if  len(lines_vert)<2:
            thrs = int(thrs*0.9)
            continue
        # Neste ponto, temos ao menos duas linhas
        # Pega linhas externas
        lines_vert = sorted(lines_vert, key = lambda line : abs(line[0][0]))
        left_line = lines_vert[0] # linha com menor raio é a mais próxima da esquerda
        right_line = lines_vert[-1]

        # Verifica se não faz sentido (linha esquerda não está +- na esquerda e não é vertical)
        if abs(left_line[0][0]) > 0.33*width or abs(right_line[0][0]) < 0.66*width:
            thrs = int(thrs*0.9)
            continue

        # Neste ponto, achou linhas
        found_vert_lines = True
        left_line = convert_polar_to_cartesian(left_line[0][0],left_line[0][1])
        right_line = convert_polar_to_cartesian(right_line[0][0],right_line[0][1])


    # Acha linhas superior e inferior
    thrs=int(width*0.4) # a linha deve ter ao menos 1/2 do tamanho vertical
    found_horiz_lines = False
    while not found_horiz_lines:
        lines_horiz = cv2.HoughLines(img_filt_horiz, 1, np.pi / 720, thrs)
        if lines_horiz is None:
            thrs = int(thrs*0.9)
            continue
        if  len(lines_horiz)<2:
            thrs = int(thrs*0.9)
            continue
        # Neste ponto, temos ao menos duas linhas
        # Pega linhas externas
        lines_horiz = sorted(lines_horiz, key = lambda line : abs(line[0][0]))
        top_line = lines_horiz[0] # linha com menor raio é a mais próxima do topo
        botton_line = lines_horiz[-1]

        # Verifica se não faz sentido (linha topo não está +- no topo e não é horizontal)
        if abs(top_line[0][0]) > 0.33*height or abs(botton_line[0][0]) < 0.66*height:
            thrs = int(thrs*0.9)
            continue

        # Neste ponto, achou linhas
        found_horiz_lines = True
        top_line = convert_polar_to_cartesian(top_line[0][0],top_line[0][1])
        botton_line = convert_polar_to_cartesian(botton_line[0][0],botton_line[0][1])


    if DEBUG:
        hough_result = cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
        xyLines_vert = [convert_polar_to_cartesian(line[0][0],line[0][1]) for line in lines_vert]
        xyLines_horiz = [convert_polar_to_cartesian(line[0][0],line[0][1]) for line in lines_horiz]
        for line in xyLines_vert:
            cv2.line(hough_result, (line[0], line[1]), (line[2], line[3]), (0,0,255), 2, cv2.LINE_AA)
        for line in xyLines_horiz:
            cv2.line(hough_result, (line[0], line[1]), (line[2], line[3]), (255,0,0), 2, cv2.LINE_AA)      
        show_wait_destroy(hough_result,"hough result",scale=0.2)


    if DEBUG :
        final_result = cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
        cv2.line(final_result, (top_line[0], top_line[1]), (top_line[2], top_line[3]), (255,255,0), 2, cv2.LINE_AA)
        cv2.line(final_result, (botton_line[0], botton_line[1]), (botton_line[2], botton_line[3]), (0,255,0), 2, cv2.LINE_AA)
        cv2.line(final_result, (left_line[0], left_line[1]), (left_line[2], left_line[3]), (255,0,0), 2, cv2.LINE_AA)
        cv2.line(final_result, (right_line[0], right_line[1]), (right_line[2], right_line[3]), (0,0,255), 2, cv2.LINE_AA)
        show_wait_destroy(final_result,"final lines",scale=0.2)

     # Geting intersection points
    #up-left point
    x, y = line_intersection(top_line, left_line)
    pt1 = [x,y]
    #up-right point 
    x, y = line_intersection(top_line, right_line)
    pt2 = [x,y]
    #bottom-right point
    x, y = line_intersection(botton_line, right_line)
    pt3 = [x,y]
    #bottom-left point 
    x, y = line_intersection(botton_line, left_line)
    pt4 = [x,y]
    points = [pt1, pt2, pt3, pt4 ]

    # Adjust img
    findedPoints = np.array([points])
    left_margin =int(width*0.07)
    top_margin = int(height*0.06)
    form_width = int(width*0.86)
    form_ratio = 0.7 # a transformação deve manter a proporção do form
    if width > height: #landscape
        form_height = int(form_width*form_ratio)
    else:
        form_height = int(form_width/form_ratio)
    desiredPoints = np.array([  [left_margin, top_margin],                 # top-left
                                [left_margin+form_width, top_margin] ,          # top-right
                                [left_margin+form_width, top_margin+form_height],    # bottom-right
                                [left_margin, top_margin+form_height]])         # bottom-left
    h, _ = cv2.findHomography(findedPoints, desiredPoints, cv2.RANSAC)
    adjusted = cv2.warpPerspective(img, h, (width, height),borderValue=(255,255,255))

    if DEBUG :
        show_wait_destroy(adjusted,"final result",scale=0.2)
    
    return adjusted
    

def line_coef(p1, p2):
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0]*p2[1] - p2[0]*p1[1])
    return A, B, -C

def line_intersection(line1, line2):
    L1 = line_coef(line1[0:2], line1[2:])
    L2 = line_coef(line2[0:2], line2[2:])
    D  = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return x,y
    else:
        return False

def getCoef(line):
    if(line[2]-line[0] == 0):
        return 0, True
    m = (line[3] - line[1]) / (line[2] - line[0])
    return m, False


def getIntersectionPoint(lineA, lineB):
    ma, statusA = getCoef(lineA)
    mb, statusB = getCoef(lineB)

    if statusA:
        x = lineA[0]
        y = mb*(x-lineB[0]) + lineB[1]
        return int(x), int(y)
    
    if statusB:
        x = lineB[0]
        y = mb*(x-lineA[0]) + lineA[1]
        return int(x), int(y)

    x = mb*lineB[0] + lineA[1] - ma*lineA[0] - lineB[1]
    x = x / (mb-ma)

    y = ma*(x - lineA[0]) + lineA[1]

    return int(x), int(y)

def convert_polar_to_cartesian(rho,theta):
    # Convert a cartesian line to two points in the line [x_1, y_1, x_2, y_2]
    xyLine = [0,0,0,0]
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a*rho
    y0 = b*rho
    xyLine[0] = int(x0 + 30000*(-b))
    xyLine[1] = int(y0 + 30000*a)
    xyLine[2] = int(x0 - 30000*(-b))
    xyLine[3] = int(y0 - 30000*a)
    return xyLine

def show_wait_destroy(img,winname="image",normalize=False,scale=1,save=True):
    # Mostra uma imagem opencv
    # normalize - reescala os valores da imagem para ficar entre 0 e 255
    # scale - zoom
    # save - salva uma imagem jpg com o nome da janela
    if normalize:
        show_img  = np.copy(img)
        show_img = cv2.normalize(img,  show_img, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    else:
        show_img = img

    if save:
        cv2.imwrite(winname + ".jpg",show_img)

    cv2.namedWindow(winname, cv2.WINDOW_NORMAL)
    cv2.imshow(winname, show_img)

    if scale != 1:
        cv2.resizeWindow(winname, int(show_img.shape[1]*scale), int(show_img.shape[0]*scale))
    cv2.waitKey(0)
    cv2.destroyWindow(winname)

if __name__ == "__main__":
    import pdf2image
    # file_ = "D:\\temp\\tot\\databooks\\DATA BOOK S-276 - 28-01-2019\\Parte G - Relatórios de Inspeções (Tubulação)\\3 - Relatório de Partícula Magnética;\\3 - Partículas Magnéticas.pdf"
    # file_ = "D:\\temp\\tot\\databooks\\DATA BOOK S-276 - 28-01-2019\\Parte G - Relatórios de Inspeções (Tubulação)\\1 - Relatório Dimensional;\\1.2 - Dimensional Final;\\1.2 - Dimensional Final;.pdf"
    file_ = "D:\\temp\\tot\\databooks\\DATA BOOK S-276 - 28-01-2019\\Parte G - Relatórios de Inspeções (Tubulação)\\2 - Relatório Visual;\\2.2 - Visual Final;\\2.2 - Visual Final;.pdf"
    # file_ = "D:\\temp\\tot\\databooks\\DATA BOOK S-276 - 28-01-2019\\Parte G - Relatórios de Inspeções (Tubulação)\\5 - Relatório de Ultrassom Phased Array Radiografia\\5 - Relat. de Ultr. Ph. Arr. RX.pdf"
    pages = pdf2image.convert_from_path(file_,first_page=133, last_page=133,dpi=300,fmt='png')
    for img in pages:
        img_np = np.asarray(img)
        preprocess_enaval_form(img_np, DEBUG=True)