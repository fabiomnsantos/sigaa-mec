# Automação SIGAA – Relatórios para Avaliação MEC

## Objetivo

Este conjunto de scripts automatiza a coleta, organização e consolidação dos documentos das turmas do SIGAA necessários para processos de avaliação institucional (MEC, INEP, reconhecimento e renovação de cursos).

O sistema realiza automaticamente:

* Descoberta das turmas ministradas pelo docente;
* Download dos Planos de Curso;
* Download dos Diários de Turma;
* Identificação dos cursos atendidos por cada turma;
* Organização dos documentos por curso;
* Geração de relatórios consolidados em PDF.

---

# Estrutura do Projeto

```text
.
├── gerar_turmas_csv.py
├── baixar_todas_turmas.py
├── organizar_sigaa.py
├── gerar_relatorio.py
├── .env
├── turmas.csv
├── downloads_sigaa/
└── turmas_passadas_sigaa/
```

---

# Dependências

Instalar:

```bash
pip install playwright pandas python-dotenv pypdf
```

Instalar o navegador do Playwright:

```bash
playwright install chromium
```

---

# Configuração

Criar um arquivo `.env`:

```text
SIGAA_USER=seu_usuario_SIGAA
SIGAA_PASS=sua_senha_SIGAA
```

---

# Fluxo Completo

## Passo 1 – Descobrir as turmas

Executar:

```bash
python gerar_turmas_csv.py
```

O script:

1. Faz login no SIGAA;
2. Abre a página de turmas;
3. Identifica todas as turmas ministradas;
4. Gera:

```text
turmas.csv
```

Exemplo:

```csv
codigo,disciplina,periodo,turma
UAB00006,FÍSICA GERAL 1,2025.1,04
UAB00007,FÍSICA GERAL 2,2025.1,02
...
```

---

## Passo 2 – Baixar documentos

Executar:

```bash
python baixar_todas_turmas.py
```

O script:

1. Faz login no SIGAA;

2. Percorre todas as turmas do arquivo `turmas.csv`;

3. Abre automaticamente cada turma;

4. Baixa:

   * Diário de Turma
   * Plano de Curso

5. Abre a página de Participantes;

6. Identifica os cursos presentes na turma;

7. Atualiza continuamente:

```text
downloads_sigaa/turmas_mestre.csv
```

---

## Arquivos gerados

```text
downloads_sigaa/

Plano_de_Curso_UAB00006_2025.1_04_.pdf
Plano_de_Curso_UAB00007_2025.1_02_.pdf

diario_UAB00006_2025.1_04_.pdf
diario_UAB00007_2025.1_02_.pdf

turmas_mestre.csv
```

---

## Retomada automática

O script verifica se os arquivos já existem.

Exemplo:

```text
Já existe: diario_UAB00006_2025.1_04_.pdf
```

Nesse caso o download é ignorado.

Isso permite interromper e retomar o processo a qualquer momento.

---

# Passo 3 – Organizar documentos por curso

Executar:

```bash
python organizar_sigaa.py
```

O script utiliza:

```text
downloads_sigaa/
turmas_mestre.csv
```

para organizar os documentos em:

```text
turmas_passadas_sigaa/

PorCurso/

├── Computacao/
├── Controle/
├── Quimica/
└── Hidrica/
```

Estrutura exemplo:

```text
Computacao/
└── 2025.1/
    └── Física Geral 1/
        ├── Plano_de_Curso...
        └── diario...
```

---

# Passo 4 – Gerar relatório consolidado

Executar:

```bash
python gerar_relatorio.py Computacao
```

ou

```bash
python gerar_relatorio.py Controle
```

ou

```bash
python gerar_relatorio.py Quimica
```

ou

```bash
python gerar_relatorio.py Hidrica
```

Também é possível informar períodos específicos.

Exemplo:

```bash
python gerar_relatorio.py Hidrica 2024.1 2024.2 2025.1
```

---

# Relatório Gerado

O relatório final contém 2 PDFs:

1. Todos os Planos de Curso;
2. Todos os Diários de Turma.

---

# Cursos Detectados

Atualmente o sistema identifica automaticamente:

```text
Computacao
Controle
Quimica
Hidrica
```

Correspondentes a:

```text
ENGENHARIA DA COMPUTAÇÃO
ENGENHARIA DE CONTROLE E AUTOMAÇÃO
ENGENHARIA QUÍMICA
ENGENHARIA HÍDRICA
```

---

# Recuperação de Falhas

O script principal possui:

* Continuação automática após erro em uma turma;
* Salvamento incremental do CSV mestre;
* Ignora downloads já realizados.

Assim, uma falha em uma turma não interrompe o processamento das demais.

---

# Fluxo Resumido

```text
gerar_turmas_csv.py
          ↓
      turmas.csv
          ↓
baixar_todas_turmas.py
          ↓
downloads_sigaa/
          ↓
organizar_sigaa.py
          ↓
turmas_passadas_sigaa/
          ↓
gerar_relatorio.py
          ↓
PDFs finais para MEC
```

---

# Autor

Prof. Fábio Novaes
UABJ / UFRPE

## Observação

Este projeto foi desenvolvido com auxílio do ChatGPT (OpenAI) para geração e refinamento de partes do código, 
documentação e automação de tarefas. Todo o código foi revisado, adaptado e validado pelo autor antes de sua utilização.

## Licença

Este projeto é distribuído sob a licença MIT. Consulte o arquivo LICENSE para mais detalhes.