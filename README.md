# ⚡️ Lightning Talks on Discord

## Rodando robô localmente
- Variáveis de ambiente necessárias estão definidas em `local.env`. Copie o arquivo `local.env` para `.env` e adicione os valores necessários.
- O banco de dados usado no projeto é o `MongoDB`.
- Execute `docker run -d -p 27017:27017 mongo` para criar uma instância localmente (sem volume/persistentes dos dados salvos no banco), e defina `localhost` na variável `DATABASE_URL` no arquivo `.env`.
