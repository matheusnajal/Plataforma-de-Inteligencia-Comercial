![Python](https://img.shields.io/badge/python-000000?style=for-the-badge&logo=python&logoColor=white)
![Requests](https://img.shields.io/badge/requests-000000?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-000000?style=for-the-badge&logo=pandas&logoColor=white)
![Streamlit](https://img.shields.io/badge/streamlit-000000?style=for-the-badge&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/plotly-000000?style=for-the-badge&logo=plotly&logoColor=white)

# Plataforma de Inteligencia Comercial

## Objetivo
Fornecer uma visão clara de KPIs cruciais (Receita, Volume e Ticket Médio), permitindo que gestores tomem decisões baseadas em dados através de filtros dinâmicos de região, período e performance de vendedores.

## Diferenciais Técnicos e Funcionalidades
- **Otimização de Performance**: Utilização de `st.cache_data` com TTL (Time-To-Live) para reduzir o overhead de requisições à API e acelerar a experiência do usuário.
- **Design Profissional (Dark Theme)**: Interface customizada via `.streamlit/config.toml` para um visual sóbrio e moderno, ideal para ambientes corporativos.
- **Visualização Geoespacial**: Mapas de dispersão geográfica (`scatter_geo`) para identificação imediata de polos de receita na América do Sul.
- **Análise Multidimensional**:
    - **Visão de Receita**: Evolução mensal, distribuição por categorias e top estados.
    - **Visão de Volume**: Quantidade de transações e sazonalidade.
    - **Ranking de Vendedores**: Análise competitiva de performance individual.
- **Tratamento de Erros**: Implementação de blocos `try-except` para garantir que a aplicação não apresente falhas em caso de instabilidade na API de dados.

## Estrutura do Repositório
```text
├── .streamlit/
│   └── config.toml          # Definições de cores e tema Dark
├── pages/
│   └── Dados_Brutos.py      # Página de exportação e filtragem tabular
├── Dashboard.py             # Aplicação principal (UI/UX e Gráficos)
├── requirements.txt         # Dependências do projeto
└── README.md                # Documentação
```

## Acessar a Aplicação em Produção
**[Dashboard Online](https://matheusnajal-dashboard.streamlit.app/)**