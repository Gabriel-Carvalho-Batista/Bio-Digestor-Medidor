# Contrato da API — Estação de Medição

Documento pra quem for programar o Arduino/ESP saber exatamente como
enviar os dados pro servidor.

## Endpoint

```
POST https://SEU-APP.onrender.com/dados
```

(Trocar `SEU-APP` pela URL real depois que o serviço for criado no Render.)

## Cabeçalhos obrigatórios

```
Content-Type: application/json
```

## Corpo da requisição (JSON)

Campos atuais:

| Campo         | Tipo   | Obrigatório | Descrição              |
|---------------|--------|--------------|-------------------------|
| `temperatura` | número | sim          | Temperatura em °C       |
| `umidade`     | número | sim          | Umidade relativa em %   |

Exemplo:

```json
{
  "temperatura": 24.6,
  "umidade": 58.2
}
```

### Campo futuro (medidor de fluxo)

Quando o sensor de fluxo for adicionado, basta incluir mais um campo,
sem quebrar nada do que já existe:

```json
{
  "temperatura": 24.6,
  "umidade": 58.2,
  "fluxo": 3.75
}
```

| Campo   | Tipo   | Obrigatório | Descrição                        |
|---------|--------|--------------|------------------------------------|
| `fluxo` | número | não          | Vazão medida (unidade a definir)  |

## Respostas

| Status | Significado                                      |
|--------|---------------------------------------------------|
| `201`  | Leitura salva com sucesso                          |
| `400`  | JSON ausente/inválido, ou faltando campo obrigatório |

Corpo de resposta em caso de sucesso:
```json
{ "status": "ok" }
```

Corpo de resposta em caso de erro:
```json
{ "erro": "descrição do problema" }
```

## Frequência recomendada de envio

Uma leitura a cada **60 segundos** é suficiente pro propósito do site.
Enviar com mais frequência que isso não traz benefício visual e
consome mais dados/bateria à toa.

## Consultando os dados (rota usada pelo site, não pelo Arduino)

```
GET https://SEU-APP.onrender.com/dados?limite=100
```

Retorna as últimas N leituras (padrão 100) em ordem cronológica,
cada uma com `id`, `temperatura`, `umidade`, `fluxo` e `timestamp`
(UTC, formato ISO 8601).
