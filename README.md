
# Chat com AI usando Flask e OpenRouter

Este projeto é uma aplicação web simples que permite interagir com diferentes modelos de AI disponíveis no OpenRouter. Utiliza o framework Flask para criar a interface e faz pedidos à API do OpenRouter para obter respostas.

---

## **Requisitos**

- Python 3.8 ou superior.
- Conta no [OpenRouter](https://openrouter.ai/) para obter uma chave da API.

---

## **Instalação**

1. Clone este repositório:
   ```bash
   git clone https://github.com/seu-usuario/nome-do-repositorio.git
   cd nome-do-repositorio
   ```

2. Crie um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

---

## **Configuração**

1. Crie um ficheiro `.env` na raiz do projeto e adicione as seguintes variáveis de ambiente:
   ```plaintext
   OPENROUTER_API_KEY=sua_chave_api_aqui
   YOUR_SITE_URL=https://seusite.com
   YOUR_SITE_NAME=Meu Site
   ```
   - Substitua `sua_chave_api_aqui` pela sua chave de API do OpenRouter.
   - Substitua `https://seusite.com` pela URL do seu site.
   - Substitua `Meu Site` pelo nome do seu site.

2. Guarde o ficheiro `.env`.

---

## **Executar o Projeto**

1. Inicie o servidor Flask:
   ```bash
   python app.py
   ```

2. Aceda à aplicação no navegador:
   ```
   http://127.0.0.1:5000
   ```

---

## **Como Utilizar**

1. Na página inicial, insira a sua pergunta no campo "Pergunta".
2. (Opcional) Adicione o URL de uma imagem no campo "URL da Imagem".
3. Selecione a AI desejada no menu suspenso.
4. Clique em "Enviar" para obter a resposta.

---

## **Estrutura do Projeto**

```
projeto/
│
├── app.py                 # Ficheiro principal da aplicação Flask
├── requirements.txt       # Lista de dependências do projeto
├── .env                   # Ficheiro de variáveis de ambiente
├── README.md              # Documentação do projeto
└── templates/             # Pasta para os templates HTML
    └── index.html         # Template da página inicial
```

---

## **Dependências**

- **Flask**: Framework web para criar a aplicação.
- **requests**: Biblioteca para fazer pedidos HTTP à API do OpenRouter.
- **python-dotenv**: Biblioteca para carregar variáveis de ambiente de um ficheiro `.env`.

---

## **Contribuição**

Se quiser contribuir para este projeto, siga os passos abaixo:

1. Faça um fork do repositório.
2. Crie uma branch para a sua funcionalidade:
   ```bash
   git checkout -b minha-funcionalidade
   ```
3. Faça commit das suas alterações:
   ```bash
   git commit -m "Adicionando nova funcionalidade"
   ```
4. Envie para o repositório remoto:
   ```bash
   git push origin minha-funcionalidade
   ```
5. Abra um pull request.

---

## **Licença**

Este projeto está licenciado sob a licença MIT. Consulte o ficheiro [LICENSE](LICENSE) para mais detalhes.

---

## **Contacto**

Se tiver dúvidas ou sugestões, entre em contacto:

- **Nome**: [Diogo Pacheco]
- **Email**: [diogopacheco132@gmail.com]
- **GitHub**: [https://github.com/dspacheco132]

