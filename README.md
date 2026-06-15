# Py DNS Changer

Um aplicativo leve e prático para o Windows que reside na bandeja do sistema (System Tray) e permite alternar rapidamente os servidores DNS das suas interfaces de rede ativas.

## 🚀 Funcionalidades

- **Acesso Rápido pela Bandeja**: Troque de DNS com apenas dois cliques através do ícone oculto na barra de tarefas.
- **Gestão Dinâmica de DNS**: Adicione, edite ou remova perfis de DNS (como Google, Cloudflare, OpenDNS) usando uma interface gráfica embutida.
- **Seleção de Interface de Rede**: Identifica automaticamente suas placas de rede ativas para você escolher onde aplicar as mudanças.
- **Tela de Status da Rede**: Veja todas as suas configurações IP atuais (`ipconfig /all`) rapidamente em uma interface de texto dentro do aplicativo.
- **Auto-Elevação**: O aplicativo solicita privilégios de Administrador automaticamente (necessário para alterar configurações do Windows usando `netsh`).
- **Configurações Persistentes**: Seus perfis de DNS favoritos ficam salvos automaticamente no arquivo `dns_config.json`.

## 🛠️ Tecnologias e Dependências

Este projeto foi construído em Python e utiliza o [uv](https://github.com/astral-sh/uv) como gerenciador de pacotes.

- **Python**: `>=3.12`
- **Sistema Operacional**: Windows (o script usa APIs `win32` e o comando `netsh`).
- **Bibliotecas Principais**:
  - `pystray`: Gerenciamento do ícone na bandeja do sistema.
  - `psutil`: Mapeamento das interfaces de rede ativas.
  - `Pillow`: Geração e controle da imagem do ícone.
  - `tkinter`: Interface gráfica para gerenciamento de DNS e Status da rede.

## 📦 Instalação e Execução

### Rodando o código fonte

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/py-dns-changer.git
   cd py-dns-changer
   ```

2. **Instale as dependências (recomendamos usar o `uv`):**
   ```bash
   uv sync
   ```
   *(Caso não use o `uv`, você pode criar um `.venv` e instalar os pacotes via pip)*.

3. **Execute o projeto:**
   ```bash
   .venv\Scripts\python main.py
   ```

## 🏗️ Compilando (Gerando o arquivo .EXE)

Para compilar o código em um arquivo executável único (sem necessidade de ter o Python instalado na máquina de destino), você pode utilizar o **PyInstaller**.

Execute o seguinte comando na raiz do projeto:

```bash
.venv\Scripts\pyinstaller --noconsole --onefile main.py
```

- O executável será gerado dentro da pasta `dist/` com o nome `main.exe`.
- Como usamos o argumento `--noconsole`, o programa rodará silenciosamente na bandeja do sistema.

## ⚙️ Como Funciona

1. Ao abrir o programa (ou o `.exe`), ele checará se tem direitos de **Administrador**. Caso não tenha, ele solicitará a permissão na tela (UAC).
2. O ícone 🔵 surgirá na sua bandeja do sistema (perto do relógio do Windows).
3. **Clique com o botão direito** no ícone para acessar o menu:
   - **Selecionar Interface**: Escolha o seu adaptador de rede (ex: Wi-Fi ou Ethernet).
   - **Selecionar DNS**: Submenu para escolher o perfil de DNS que será aplicado. O perfil em uso ficará marcado.
   - **Gerenciar DNS...**: Abre a tela para você cadastrar seus servidores favoritos.
   - **Status da Rede...**: Mostra informações completas do console de rede do Windows.

## 📝 Licença

Desenvolvido para facilitar o fluxo de trabalho local. Sinta-se à vontade para realizar um "fork", enviar "pull requests" ou adaptar o código conforme a sua necessidade!
