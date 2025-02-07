# Treinamento do modelo

Dentro deste diretório, temos todos os arquivos necessários para realizar o treinamento do modelo.

O modelo utilizado nessa aplicação, foi treinado a partir de um dataset criado especialmente para esse trabalho, contendo mais de 7000 imagens de armas como granadas, armas de fogo longas, facas e pistolas.

O Dataset está disponível nesse link: https://universe.roboflow.com/fiapiadt/hackathon-689ec

O modelo base utilizado para treinar o modelo dessa aplicação, a partir do dataset acima, foi o [YOLOv11](https://docs.ultralytics.com/tasks/detect/)


## Como treinar o modelo:

Para treinar o modelo utilizado nessa aplicação nós utilizamos o Google Colab. Para reproduzir o treinamento, siga os passos abaixo:

1. Copie todo o conteúdo do diretório `model_training` para o google drive. Na raiz do google Drive, crie uma pasta chamada `FIAP`.
2. Baixe o dataset desse link: https://universe.roboflow.com/fiapiadt/hackathon-689ec e faça o upload das imagens no google drive dentro das pastas corretas em `train/data`. 
```
model_training/
├── data/
│   ├── train/
│   │   ├── images
│   │   ├── labes
│   ├── val/
│   │   ├── images
│   │   ├── labels
│   ├── test/
│   │   ├── images
│   │   ├── labels
```
3. Ajuste os caminhos dentro do Notebook

4. Execute o notebook

5. O modelo será salvo no Drive, em `/runs/detect/best_xxxx/weights/best.pt`
