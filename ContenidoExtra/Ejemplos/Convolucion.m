% =========================================================================
% Script de MATLAB para Convolución de Imágenes
% =========================================================================

% 1. Cargar la imagen elegida
% Sustituye 'mi_foto.jpg' por el nombre de tu archivo de imagen
nombre_archivo = 'ejemplo.jpg'; 
img = imread(nombre_archivo);

% 2. Convertir a escala de grises (las CNN suelen empezar así)
% Comprobamos si la imagen tiene 3 canales (RGB)
if size(img, 3) == 3
    img_gray = rgb2gray(img);
else
    img_gray = img;
end

% 3. Normalizar la imagen
% Convertimos los píxeles (0-255) a formato 'double' (0.0 a 1.0) 
% Esto es crucial para que las matemáticas de la convolución no den error
img_double = im2double(img_gray);

% 4. Definir el Filtro (Kernel)
% Aquí puedes descomentar (quitar el %) del filtro que quieras probar:

% Opción A: Filtro Detector de Bordes (Resalta los contornos)
kernel = [-1 -1 -1; 
          -1  8 -1; 
          -1 -1 -1];

% Opción B: Filtro de Desenfoque / Blur (Suaviza la imagen)
% kernel = (1/9) * [1 1 1; 
%                   1 1 1; 
%                   1 1 1];

% Opción C: Filtro de Realce / Sharpen (Hace la imagen más nítida)
% kernel = [ 0 -1  0; 
%           -1  5 -1; 
%            0 -1  0];

% 5. Aplicar la Convolución
% Utilizamos 'conv2' para convolución en 2D. 
% El parámetro 'same' asegura que la imagen final mantenga el mismo tamaño original.
imagen_convolucionada = conv2(img_double, kernel, "valid");

% 6. Visualizar los resultados
figure('Name', 'Explorador de Convolución', 'NumberTitle', 'off');

% Mostrar imagen original
subplot(1, 2, 1);
imshow(img_gray);
title('Imagen Original (Escala de Grises)');

% Mostrar imagen tras la convolución
subplot(1, 2, 2);
imshow(imagen_convolucionada);
title('Resultado del Filtro (Feature Map)');