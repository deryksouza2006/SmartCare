# 🐾 PetJourney SmartCare

Microserviço inteligente de **priorização de acompanhamento de pets**, desenvolvido como parte do ecossistema PetJourney para o Challenge 2026 da FIAP.

O SmartCare analisa informações clínicas previamente consolidadas pelo backend do PetJourney e retorna uma prioridade operacional para auxiliar veterinários e administradores de clínicas na identificação de pets que podem necessitar de maior atenção.

> O SmartCare é uma ferramenta de apoio à decisão. Ele não realiza diagnóstico veterinário e não substitui a avaliação de um médico-veterinário.

## Integrantes

| Nome | RM |
|---|---|
| Lucas Gonçalves Viana | 563254 |
| Deryk de Souza Queiroz | 563412 |
| Vinicius Paschoeto da Silva | 563089 |
| Felipe Wiclif Leal da Silva | 563901 |

---

## 🔗 Links da entrega

| Item | Link |
|---|---|
| Vídeo no YouTube | A inserir após a gravação |
| Repositório SmartCare | [github.com/deryksouza2006/SmartCare](https://github.com/deryksouza2006/SmartCare) |
| Repositório Mobile | [github.com/deryksouza2006/PetJourney2.0](https://github.com/deryksouza2006/PetJourney2.0) |
| Repositório Backend Java | [github.com/LucasViana130/api-java-petjourney](https://github.com/LucasViana130/api-java-petjourney) |
| Deploy SmartCare — Swagger | [Abrir documentação interativa](https://petjourney-smartcare.onrender.com/docs) |
| Deploy SmartCare — Health Check | [Verificar disponibilidade](https://petjourney-smartcare.onrender.com/health) |
| Deploy API Java — Swagger | [Abrir documentação da API principal](https://petjourney-api.onrender.com/swagger-ui.html) |

> A rota raiz do SmartCare não possui uma página visual. Para validar o deploy, utilize o Swagger ou o Health Check nos links acima.

---

## 🎯 Objetivo

Uma clínica veterinária pode possuir diversos pacientes em diferentes situações:

- pets atendidos recentemente;
- pets há vários meses sem acompanhamento;
- pets sem nova consulta agendada;
- pets em tratamento sem retorno programado.

A análise manual desses casos pode dificultar a identificação dos pacientes que precisam de acompanhamento prioritário.

O SmartCare foi desenvolvido para transformar essas informações em uma classificação simples, explicável e útil para a rotina da clínica.

---

## 🧠 Abordagem utilizada

O SmartCare utiliza um **motor de regras inteligentes determinístico**.

Nesta versão, não são utilizados:

- modelos de Machine Learning;
- LLMs;
- IA generativa;
- APIs externas de Inteligência Artificial.

A estratégia adotada permite que toda classificação seja:

- previsível;
- reproduzível;
- testável;
- explicável;
- baseada diretamente nos dados clínicos do PetJourney.

O resultado não apresenta apenas uma prioridade: o sistema também informa os fatores que contribuíram para aquela classificação.

---

# 🏗️ Arquitetura da solução

O SmartCare faz parte de uma arquitetura maior dentro do PetJourney.

```text
┌──────────────────────┐
│   Mobile PetJourney  │
│ React Native + Expo  │
└──────────┬───────────┘
           │ HTTP
           ▼
┌──────────────────────┐
│   API PetJourney     │
│ Java + Spring Boot   │
└──────────┬───────────┘
           │
           ├──────────────► PostgreSQL
           │                 Dados clínicos
           │
           ▼
┌──────────────────────┐
│      SmartCare       │
│ Python + FastAPI     │
│ Motor de regras      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   API Spring Boot    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Mobile PetJourney  │
└──────────────────────┘
```

### Fluxo simplificado

```text
Mobile
   ↓
Spring Boot
   ↓
PostgreSQL
   ↓
Spring consolida os dados
   ↓
SmartCare
   ↓
Spring Boot
   ↓
Mobile
```

O aplicativo Mobile **não acessa o SmartCare diretamente**.

O backend Java é responsável por:

- autenticação;
- autorização;
- acesso ao banco de dados;
- preparação dos dados;
- chamada ao SmartCare;
- validação da resposta;
- tratamento de erros;
- entrega do resultado ao aplicativo.

Essa separação mantém o SmartCare focado exclusivamente na análise inteligente.

---

# 📊 Dados utilizados

O microserviço recebe quatro informações:

```json
{
  "petId": 123,
  "dataUltimoAtendimento": "2025-08-06",
  "possuiProximoAgendamento": false,
  "possuiTratamentoRegistrado": true
}
```

### `petId`

Identificador do pet analisado.

Deve ser um número inteiro positivo.

### `dataUltimoAtendimento`

Data do último atendimento clínico registrado.

Datas futuras não são aceitas.

### `possuiProximoAgendamento`

Indica se existe uma consulta futura programada.

### `possuiTratamentoRegistrado`

Indica se existe tratamento registrado para o pet.

Essas informações são obtidas e consolidadas pelo backend Java a partir dos dados existentes no PetJourney.

O SmartCare:

- não acessa diretamente o PostgreSQL;
- não altera registros clínicos;
- não persiste análises;
- não gerencia autenticação.

---

# ⚙️ Regras de priorização

O SmartCare atribui uma pontuação entre **0 e 100**.

## Tempo desde o último atendimento

| Período | Pontuação |
|---|---:|
| Até 90 dias | 0 |
| 91 a 180 dias | +10 |
| 181 a 365 dias | +30 |
| Mais de 365 dias | +60 |

Os motivos retornados pelo sistema podem incluir:

```text
Mais de 90 dias desde o último atendimento
```

```text
Mais de 180 dias desde o último atendimento
```

```text
Longo período sem atendimento registrado
```

---

## Sem próximo agendamento

Caso o pet não possua uma próxima consulta:

```text
+20 pontos
```

Motivo:

```text
Não possui próximo agendamento
```

---

## Tratamento sem retorno

Quando existe um tratamento registrado e não existe um próximo agendamento:

```text
+20 pontos
```

Motivo:

```text
Existe tratamento registrado sem retorno agendado
```

---

## Limite

O score máximo é:

```text
100
```

Mesmo quando a soma das regras ultrapassa esse valor.

---

# 🚦 Classificação

A partir do score final, o SmartCare define uma prioridade.

| Score | Prioridade |
|---|---|
| 0 a 29 | `BAIXA` |
| 30 a 59 | `MEDIA` |
| 60 a 100 | `ALTA` |

---

# 💡 Recomendações

Além do score, prioridade e motivos, o SmartCare retorna uma recomendação operacional.

### Prioridade BAIXA

```text
Manter acompanhamento conforme planejamento atual
```

### Prioridade MEDIA

```text
Revisar o acompanhamento do pet e avaliar necessidade de retorno
```

### Prioridade ALTA

```text
Entrar em contato com o tutor para retomar o acompanhamento
```

Essas recomendações são operacionais e não constituem diagnóstico veterinário.

---

# 🔎 Exemplo completo

## Requisição

```http
POST /smartcare/analisar
Content-Type: application/json
```

```json
{
  "petId": 123,
  "dataUltimoAtendimento": "2025-08-06",
  "possuiProximoAgendamento": false,
  "possuiTratamentoRegistrado": true
}
```

## Resposta possível

```json
{
  "petId": 123,
  "score": 100,
  "prioridade": "ALTA",
  "motivos": [
    "Longo período sem atendimento registrado",
    "Não possui próximo agendamento",
    "Existe tratamento registrado sem retorno agendado"
  ],
  "recomendacao": "Entrar em contato com o tutor para retomar o acompanhamento"
}
```

---

# 🔌 API SmartCare

O microserviço possui dois endpoints.

## Health Check

```http
GET /health
```

Resposta:

```json
{
  "status": "ok"
}
```

Esse endpoint permite verificar se o serviço está disponível.

---

## Analisar pet

```http
POST /smartcare/analisar
```

Executa a análise utilizando os dados recebidos.

---

# ✅ Validação dos dados

Os contratos HTTP são validados com Pydantic.

São realizadas validações como:

- `petId` deve ser inteiro;
- `petId` deve ser maior que zero;
- valores booleanos devem ser booleanos válidos;
- `dataUltimoAtendimento` deve ser uma data válida;
- `dataUltimoAtendimento` não pode estar no futuro;
- score da resposta deve permanecer entre 0 e 100.

Entradas inválidas são rejeitadas pela API com resposta HTTP apropriada, como:

```text
422 Unprocessable Entity
```

---

# ☕ Integração com o backend Java

No sistema completo, o Spring Boot realiza a integração entre o PetJourney e o SmartCare.

O aplicativo utiliza endpoints disponibilizados pela API principal, incluindo:

```http
GET /smartcare/pets/{petId}/analysis
```

para análise individual de um pet e:

```http
GET /smartcare/ranking
```

para visualização da priorização dos pacientes.

O Java obtém os dados necessários, prepara a requisição do SmartCare e processa sua resposta antes de enviá-la ao Mobile.

---

# 🔐 Controle de acesso

No fluxo oficial da aplicação, o usuário não acessa o SmartCare diretamente. O aplicativo chama a API Spring Boot, que realiza autenticação, autorização, consolidação dos dados e comunicação com o microserviço.

O deploy público do SmartCare existe para documentação, health check e demonstração acadêmica. O microserviço não acessa o banco de dados e não persiste as análises recebidas. O controle dos perfis autorizados no sistema completo permanece sob responsabilidade da API Spring Boot.

Na aplicação, o recurso SmartCare é disponibilizado para:

```text
VETERINARIO
ADMIN_CLINICA
```

O acesso não é disponibilizado diretamente para:

```text
TUTOR
ADMIN_SISTEMA
```

Essa decisão evita que uma classificação operacional seja interpretada pelo tutor como diagnóstico clínico.

---

# 📱 Integração com o Mobile

O aplicativo PetJourney apresenta os resultados do SmartCare em uma interface própria.

Entre as funcionalidades estão:

- ranking de pacientes;
- análise individual;
- score;
- prioridade;
- motivos;
- recomendação;
- identificação de casos sem dados clínicos suficientes.

O ranking permite organizar os pacientes de acordo com a necessidade de acompanhamento.

---

# 👨‍⚕️ Valor para o veterinário

O SmartCare auxilia o veterinário a identificar rapidamente:

- pacientes há muito tempo sem atendimento;
- pets sem retorno marcado;
- tratamentos sem acompanhamento futuro;
- pacientes que podem demandar maior atenção.

A decisão clínica continua sendo responsabilidade do profissional.

---

# 🏥 Valor para a clínica

Para a clínica, o SmartCare auxilia na:

- priorização de pacientes;
- organização do acompanhamento;
- utilização dos dados já registrados;
- identificação de possíveis lacunas no acompanhamento;
- continuidade do relacionamento com tutores e pets.

---

# 👤 Valor para o tutor

O Tutor não recebe diretamente a classificação técnica.

O benefício ocorre por meio da utilização do SmartCare pela clínica e pelo veterinário.

Ao identificar pacientes que podem necessitar de acompanhamento, a equipe consegue organizar melhor o cuidado e atuar de forma mais proativa na jornada do pet.

---

# 🧪 Testes

O projeto possui testes automatizados utilizando `pytest` e `HTTPX`.

A suíte atual possui testes para diferentes partes da solução.

Entre os cenários validados estão:

- prioridade baixa;
- prioridade média;
- prioridade alta;
- limites das faixas de dias;
- score máximo de 100;
- pet sem próximo agendamento;
- tratamento sem retorno;
- rejeição de datas futuras;
- validação de `petId`;
- endpoint `/health`;
- endpoint `/smartcare/analisar`;
- validações HTTP.

Execução:

```bash
pytest
```

Na validação atual do projeto:

```text
16 testes executados
16 testes aprovados
```

---

# 📂 Estrutura do projeto

```text
smartcare/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── service.py
│
├── tests/
│   └── test_smartcare.py
│
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

### `app/main.py`

Configuração do FastAPI e definição dos endpoints.

### `app/models.py`

Modelos Pydantic, contratos de entrada e saída, enum de prioridades e validações.

### `app/service.py`

Implementação do motor de regras e geração das recomendações.

### `tests/test_smartcare.py`

Testes automatizados da regra de negócio e da API HTTP.

---

# 🛠️ Tecnologias

## SmartCare

- Python 3
- FastAPI
- Pydantic
- Uvicorn

## Testes

- pytest
- HTTPX

## Ecossistema PetJourney

- React Native
- Expo
- TypeScript
- TanStack Query
- Axios
- Java 17
- Spring Boot
- Spring Security
- JWT
- PostgreSQL
- Flyway

---

# 🚀 Instalação

Execute os comandos a partir do diretório `smartcare`.

## 1. Criar ambiente virtual

```bash
python3 -m venv .venv
```

## 2. Ativar o ambiente

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

## 3. Instalar dependências

```bash
python -m pip install -r requirements.txt
```

---

# ▶️ Execução

Inicie a API:

```bash
uvicorn app.main:app --reload --port 8001
```

O SmartCare ficará disponível em:

```text
http://localhost:8001
```

---

# 📖 Swagger

A documentação interativa local pode ser acessada em:

```text
http://localhost:8001/docs
```

Em produção:

```text
https://petjourney-smartcare.onrender.com/docs
```

---

# ❤️ Health Check

Exemplo local:

```bash
curl http://localhost:8001/health
```

Em produção:

```text
https://petjourney-smartcare.onrender.com/health
```

Resposta esperada:

```json
{
  "status": "ok"
}
```

---

# 🧪 Executando os testes

Com o ambiente virtual ativado:

```bash
pytest
```

---

# 🌐 Repositórios do ecossistema

## SmartCare

```text
https://github.com/deryksouza2006/SmartCare
```

## Mobile

```text
https://github.com/deryksouza2006/PetJourney2.0
```

## Backend Java

```text
https://github.com/LucasViana130/api-java-petjourney
```

---

# 🔮 Possíveis evoluções

A arquitetura permite futuras melhorias, como:

- histórico de evolução do risco operacional;
- novos indicadores clínicos;
- acompanhamento de peso ao longo do tempo;
- identificação de padrões clínicos;
- modelos estatísticos;
- sistemas de recomendação mais avançados;
- Machine Learning com base em histórico suficiente;
- novos critérios configuráveis de priorização.

Essas funcionalidades não fazem parte da implementação atual.

---

# ⚕️ Limitações e responsabilidade

O SmartCare:

- não diagnostica doenças;
- não determina tratamentos;
- não substitui o veterinário;
- não utiliza IA generativa;
- não acessa diretamente o banco;
- não persiste análises;
- não deve ser interpretado como sistema médico autônomo.

Sua finalidade é exclusivamente fornecer **apoio operacional à tomada de decisão**, utilizando critérios objetivos definidos pelo projeto.

---
