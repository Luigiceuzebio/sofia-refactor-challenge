# Relatório de Refatoração do Projeto Sofia

Este documento detalha o processo de refatoração aplicado ao projeto Sofia, uma assistente de IA conversacional. O código original, embora funcional, estava concentrado numa única classe monolítica, o que apresentava desafios significativos para a manutenção, testabilidade e escalabilidade do projeto.

## 1. Motivação para a Refatoração

A decisão de refatorar o projeto foi motivada pela necessidade de evoluir de uma arquitetura monolítica para um design modular. A estrutura original centralizava toda a lógica de negócio, gestão de estado e interações com serviços externos num único local, resultando em:

- **Alto Acoplamento**: As diferentes responsabilidades da aplicação (ex: interagir com o SharePoint e com o Azure Boards) estavam intimamente ligadas, tornando difícil modificar uma sem impactar as outras.
- **Dificuldade de Testes**: Testar uma unidade de lógica de forma isolada era impraticável, exigindo a instanciação completa da classe e das suas múltiplas dependências.
- **Baixa Escalabilidade**: Adicionar novas funcionalidades inevitavelmente aumentaria a complexidade da classe principal, tornando o código progressivamente mais difícil de gerir.

O princípio orientador para a nova arquitetura foi a **Separação de Responsabilidades (SoC)**, com o objetivo de que cada componente do sistema tivesse um propósito único e bem definido.

## 2. A Nova Arquitetura Modular

Para alcançar os objetivos, a aplicação foi reestruturada numa nova organização de pastas, onde cada diretório e ficheiro tem uma responsabilidade clara.

### Organização em Pastas:

'''
sofia/
├── README.md # Documentação do projeto.
├── main.py # Ponto de entrada da aplicação.
├── brain.py # O orquestrador central do sistema.
│
├── core/ # Componentes centrais e transversais.
│ ├── cache.py # Gestor de cache em memória.
│ └── intent_router.py # Módulo para deteção da intenção do utilizador.
│
├── handlers/ # Módulos especializados na lógica de negócio.
│ ├── boards_handler.py # Lógica para o Azure Boards.
│ ├── file_handler.py # Lógica para o SharePoint.
│ └── general_handler.py # Lógica para interações gerais e OpenAI.
│
├── config/ # Ficheiros de configuração e conhecimento estático.
│ ├── constants.py # Constantes, palavras-chave e parâmetros.
│ └── prompts.py # Mensagens de texto e construção de prompts.
│
├── database/ # Camada de persistência de dados.
│ ├── models.py # Definição das tabelas da base de dados.
│ ├── fragments.py # Funções para consultar a base de dados.
│ └── setup.py # Script para criação da base de dados.
│
└── utils/ # Funções utilitárias genéricas.
└── helpers.py # Funções puras e reutilizáveis.
'''

## 3. Detalhes das Mudanças e Decisões

### Criação do Orquestrador (`brain.py`)

A classe `SofiaBrain` foi criada para substituir a antiga classe monolítica. A sua única função é orquestrar: inicializar todos os serviços e componentes, gerir o estado da conversação e delegar as tarefas para os módulos corretos. Esta decisão desacopla a gestão do fluxo da execução da lógica de negócio.

### Isolamento do Core (`core/`)

- A lógica de deteção de intenção foi movida para `intent_router.py`. Agora é uma função pura que recebe a mensagem e devolve uma intenção, facilitando os testes.
- O sistema de cache foi encapsulado na classe `CacheManager` em `cache.py`, tornando-o um componente reutilizável para otimizar qualquer chamada de API.

### Especialização em Handlers (`handlers/`)

- A lógica de negócio foi dividida em "manipuladores" (handlers) por domínio. O `file_handler.py` só sabe sobre ficheiros; o `boards_handler.py` só sabe sobre o Azure Boards.
- Foi adotado um padrão de **Injeção de Dependência**: os handlers não importam os serviços diretamente. Em vez disso, recebem-nos como argumentos. Isto torna-os independentes da localização dos serviços e altamente testáveis.

### Centralização do Conhecimento (`config/` e `database/`)

- **Conhecimento Estático**: Textos, comandos e parâmetros foram movidos para `config/constants.py` e `config/prompts.py`. Alterar uma mensagem de erro, por exemplo, já não exige uma modificação no código da lógica.
- **Conhecimento Dinâmico**: Foi criada uma camada de base de dados (`database/`) para armazenar o conhecimento de longo prazo da Sofia (sobre a empresa, projetos, etc.), permitindo que o seu contexto seja atualizado sem alterar o código-fonte.

### Criação de Utilitários (`utils/`)

Funções genéricas e puras, como a formatação de datas, foram movidas para `utils/helpers.py`, promovendo a reutilização de código e evitando a duplicação.

## 4. Benefícios da Refatoração

A nova arquitetura modular oferece vantagens significativas em relação à abordagem anterior:

- **Manutenibilidade**: Cada módulo é pequeno e focado, tornando a localização e correção de bugs mais rápida e segura.
- **Testabilidade**: Cada função e handler pode ser testado de forma isolada, permitindo a criação de testes unitários robustos.
- **Escalabilidade**: Adicionar uma nova funcionalidade (ex: integração com um novo serviço) resume-se a criar um novo handler e integrá-lo no `brain.py`, sem impactar os módulos existentes.
