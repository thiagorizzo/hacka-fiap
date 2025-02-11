# Hackathon FIAP IADT - Grupo 6

Esse repositório contém a solução para o desafio proposto na fase final do curso IA para Devs da FIAP.

## Desafio: FIAP VisionGuard

A FIAP VisionGuard, empresa de monitoramento de câmeras de segurança, está analisando a viabilidade de uma nova funcionalidade para otimizar o seu software.
O objetivo da empresa é usar de novas tecnologias para identificar situações atípicas e que possam colocar em risco a segurança de estabelecimentos e comércios que utilizam suas câmeras.

Um dos principais desafios da empresa é utilizar Inteligência Artificial para identificar objetos cortantes (facas, tesouras e similares) e emitir alertas para a central de segurança.

A empresa tem o objetivo de validar a viabilidade dessa feature, e para isso, será necessário fazer um MVP para detecção supervisionada desses objetos.

Objetivos
 * Construir ou buscar um dataset contendo imagens de facas, tesouras e outros objetos cortantes em diferentes condições de ângulo e iluminação;
 * Anotar o dataset para treinar o modelo supervisionado, incluindo imagens negativas (sem objetos perigosos) para reduzir falsos positivos;
 * Treinar o modelo;
 * Desenvolver um sistema de alertas (pode ser um e-mail).


## Entregável

O código desse repositório está dividido em duas partes:

1. Treinamento do modelo para detecção de armas, facas, pistolas. Se quiser reproduzir o treinamento, siga os passos nesse [Link](model_training/README.md).
2. Aplicação que utiliza o modelo treinado para deteção de armas, facas e pistolas.

Para executar a aplicação, siga os passos abaixo:

1. Instalar dependências

2. Executar src/main.py


Ao executar a aplicação, alguns passos são necessários para configurar a aplicação para que ela execute corretamente.

#### Baixar o modelo

Por conta do tamanho do arquivo, o modelo treinado não está versionado nesse repositório. A aplicação, ao ser executada, irá verificar se o modelo já foi baixado e, caso não, o modelo será baixado automaticamente a partir do google drive. Não é necessário nenhuma ação. Caso exista a necessidade de baixar manualmente o modelo, ele está disponível nesse [Link](https://drive.google.com/uc?id=1-eiFluZMyC33URgVPVAJSlB1_sWaUQVD) 


#### Configurar email

A aplicação envia emails notificando um usuário sempre que uma arma for detectada. Para isso é necessário configurar o envio de emails assim que a aplicação é executada.

A seguinte tela será exibida:

Nela é necessário informar um email e senha de remetente, utilizados para conectar a aplicação a um servidor de email. Para garantir a segurança dos dados, tanto o email como a senha não serão salvos e nem armazenados em nenhum momento.

Também é necessário informar pelo menos um email ( pode ser mais de um) de destinatário.

Ao validar e continuar, a aplicação irá testar a conexão com o servidor de email e, em caso de sucesso, a aplicação será carregada.

#### Detecção

A detecção de armas, facas e etc pode ser feita em diversas fontes como:

- Arquivo de Imagem
- Arquivo de Vídeo
- Webcam
- Feed de Câmera Online
