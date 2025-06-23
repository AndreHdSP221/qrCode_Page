# Gerador de QR Codes Sequenciais 🚥

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)

Bem-vindo ao Gerador de QR Codes Sequenciais! Este é um projeto Django desenvolvido para criar múltiplos QR codes de forma rápida e fácil, baseados em um código inicial e uma sequência numérica.

**🚀 Link para o aplicativo:** [https://qrcodesequenciais.fly.dev/](https://qrcodesequenciais.fly.dev/)

## 📸 Preview do Aplicativo

![image](https://github.com/user-attachments/assets/75a43b79-55f5-4824-9b2f-97b9d511215b)

## 📖 Descrição

Este aplicativo web permite que os usuários gerem uma série de QR codes únicos. O usuário fornece um "código base" (um prefixo) e uma "quantidade". O aplicativo então cria QR codes que combinam o código base com um número sequencial (ex: `CODIGOBASE-000001`, `CODIGOBASE-000002`, etc.). Os QR codes gerados são então disponibilizados para o usuário, prontos para download e utilização.

## 🚧 Status do Projeto e Próximos Passos

Este projeto está em **desenvolvimento ativo**. Novas funcionalidades estão sendo planejadas e serão implementadas em breve para torná-lo uma ferramenta mais completa. Os próximos passos incluem:

* **Sistema de Autenticação**: Implementação de um sistema de **login e logout** para que os usuários possam gerenciar seus QR codes.
* **Menu de Navegação**: Adição de um **menu lateral** para facilitar o acesso às diferentes funcionalidades da aplicação.
* **Novas Opções de QR Code**: Expansão para incluir outros tipos de geradores, como QR codes para vCards, redes Wi-Fi, links diretos, e mais.

## ✨ Funcionalidades Principais

* Interface web simples e intuitiva para inserção de dados.
* Geração de QR codes a partir de um código base e uma quantidade especificada.
* Criação de sequências numéricas para diferenciar cada QR code.
* Disponibilização dos QR codes gerados para download pelo usuário.

## 💻 Tecnologias Utilizadas

* **Backend:** Python com o framework Django
* **Frontend:** HTML e CSS
* **Libs:**
    * `io`: Utilizado para manipular os dados binários das imagens diretamente na memória RAM, sem a necessidade de salvar arquivos temporários no disco.
    * `zipfile`: Responsável por compactar os arquivos de QR Codes em um único arquivo `.zip`.
    * `qrcode`: A biblioteca principal para a geração dos QR Codes.
* **Hospedagem:** Fly.io

## 🚀 Como Usar (No Aplicativo Web)

1.  Acesse o aplicativo através do link: [https://qrcodesequenciais.fly.dev/](https://qrcodesequenciais.fly.dev/)
2.  No formulário apresentado:
    * Insira o **Código Base** desejado (ex: `EVENTO-ABC-LOTE1`).
    * Insira a **Quantidade** de QR codes que precisa gerar (ex: `50`).
3.  Clique no botão "Gerar QR Codes".
4.  Aguarde o processamento. Os QR codes sequenciais serão gerados e apresentados na página, prontos para serem baixados.

## 🛠️ Configuração Local (Para Desenvolvedores)

Se você deseja executar este projeto localmente para desenvolvimento ou teste:

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/AndreHdSP221/qrCode_Page.git](https://github.com/AndreHdSP221/qrCode_Page.git)
    cd qrCode_Page
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    (Recomendamos o uso do `pip-tools` para gerenciar as dependências)
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute as migrações do Django:**
    ```bash
    python manage.py migrate
    ```

5.  **Inicie o servidor de desenvolvimento:**
    ```bash
    python manage.py runserver
    ```
    O aplicativo estará geralmente acessível em `http://127.0.0.1:8000/`.

## ☁️ Deploy

Este aplicativo está atualmente hospedado na plataforma [Fly.io](https://fly.io/).

---

Feito por André Henrique
