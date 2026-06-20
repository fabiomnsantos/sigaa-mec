import re
import unicodedata
import shutil
import pandas as pd

from pathlib import Path
from pypdf import PdfReader

##############################################################################
# CONFIGURAÇÃO
##############################################################################

ENTRADA = Path("downloads_sigaa")
SAIDA = Path("turmas_passadas_sigaa")

CURSOS = {
    "ENGENHARIA DA COMPUTAÇÃO": "Computacao",
    "ENGENHARIA DE CONTROLE E AUTOMAÇÃO": "Controle",
    "ENGENHARIA QUÍMICA": "Quimica",
    "ENGENHARIA HÍDRICA": "Hidrica",
}

DISCIPLINAS = {
    "UAB00006": "Fisica Geral 1",
    "UAB00007": "Fisica Geral 2",
    "UAB00008": "Fisica Geral 3",
    "UAB00107": "Fisica Geral 4",
    "UAB00088": "Eletromagnetismo",
    "UAB00200": "Computacao Quantica",
}

##############################################################################
# LEITURA PDF
##############################################################################

def ler_pdf(pdf):

    try:

        reader = PdfReader(str(pdf))

        texto = []

        for pagina in reader.pages:

            try:

                conteudo = pagina.extract_text()

                if conteudo:
                    texto.append(conteudo)

            except Exception:
                pass

        return "\n".join(texto)

    except Exception as e:

        print(f"Erro lendo {pdf}: {e}")

        return ""


##############################################################################
# IDENTIFICAÇÃO PELO NOME DO ARQUIVO
##############################################################################

def extrair_chave_nome(nome):

    m = re.search(
        r"(UAB\d+)_(\d+\.\d)_(\d+)",
        nome,
        re.IGNORECASE
    )

    if not m:
        return None

    return (
        m.group(1),  # código
        m.group(2),  # período
        m.group(3)   # turma
    )


def identificar_tipo(nome):

    nome = nome.lower()

    if "plano" in nome:
        return "plano"

    if "diario" in nome:
        return "diario"

    if (
        "participante" in nome
        or "participantes" in nome
        or "discente" in nome
        or "discentes" in nome
    ):
        return "discentes"

    return None


##############################################################################
# EXTRAÇÃO DA DISCIPLINA
##############################################################################

def extrair_disciplina(texto):
    exto = texto.replace("\n", " ")

    m = re.search(
        r"Turma:\s*UAB\d+\s*-\s*(.*?)\s*\(\d+h\)",
        texto,
        re.IGNORECASE
    )

    if m:

        disciplina = m.group(1).strip()

        disciplina = re.sub(
            r'[<>:"/\\|?*]',
            "_",
            disciplina
        )

        return disciplina

    m = re.search(
        r"Disciplina:\s*UAB\d+\s*-\s*(.*?)(?:\(|$)",
        texto,
        re.IGNORECASE
    )

    if m:

        disciplina = m.group(1).strip()

        disciplina = re.sub(
            r'[<>:"/\\|?*]',
            "_",
            disciplina
        )

        return disciplina

    return "Disciplina_Desconhecida"


##############################################################################
# EXTRAÇÃO DOS CURSOS
##############################################################################

def normalizar(texto):

    texto = unicodedata.normalize(
        "NFKD",
        texto
    ).encode(
        "ASCII",
        "ignore"
    ).decode()

    texto = texto.upper()

    texto = texto.replace("\n", " ")

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto

def extrair_cursos(texto):

    texto = normalizar(texto)

    cursos = set()

    if "ENGENHARIA DA COMPUTACAO" in texto:
        cursos.add("Computacao")

    if "ENGENHARIA DE CONTROLE E AUTOMACAO" in texto:
        cursos.add("Controle")

    if "ENGENHARIA QUIMICA" in texto:
        cursos.add("Quimica")

    if "ENGENHARIA HIDRICA" in texto:
        cursos.add("Hidrica")

    print("\nCURSOS DETECTADOS:")
    print(cursos)

    return sorted(cursos)


##############################################################################
# INDEXAÇÃO
##############################################################################

turmas = {}

##############################################################################
# TURMAS MESTRE
##############################################################################

csv_mestre = ENTRADA / "turmas_mestre.csv"

if not csv_mestre.exists():

    raise FileNotFoundError(
        "Arquivo turmas_mestre.csv não encontrado."
    )

df_mestre = pd.read_csv(
    csv_mestre,
    dtype=str
)

mapa_cursos = {}

for _, linha in df_mestre.iterrows():

    chave = (
        linha["codigo"],
        linha["periodo"],
        linha["turma"].zfill(2)
    )

    cursos = []

    if pd.notna(linha["cursos"]):

        cursos = [
            c.strip()
            for c in linha["cursos"].split(";")
            if c.strip()
        ]

    mapa_cursos[chave] = cursos


for pdf in ENTRADA.glob("*.pdf"):

    chave = extrair_chave_nome(pdf.name)

    if chave is None:

        print(f"Ignorado (nome inválido): {pdf.name}")
        continue

    tipo = identificar_tipo(pdf.name)

    if tipo is None:

        print(f"Ignorado (tipo desconhecido): {pdf.name}")
        continue

    codigo, periodo, turma = chave

    if chave not in turmas:

        turmas[chave] = {
            "disciplina": None,
            "arquivos": {}
        }

    turmas[chave]["arquivos"][tipo] = pdf

    print(
        f"{pdf.name} -> "
        f"{tipo} | "
        f"{codigo} | "
        f"{periodo} | "
        f"{turma}"
    )

##############################################################################
# PROCESSAMENTO
##############################################################################

relatorio = []

for chave, dados in turmas.items():

    arquivos = dados["arquivos"]

    if "plano" not in arquivos:

        print(f"Sem plano: {chave}")
        continue

    if "diario" not in arquivos:

        print(f"Sem diário: {chave}")
        continue

    ##########################################################################
    # DISCIPLINA
    ##########################################################################

    texto_plano = ler_pdf(
        arquivos["plano"]
    )

    disciplina = DISCIPLINAS.get(
        chave[0],
        extrair_disciplina(texto_plano)
    )

    ##########################################################################
    # CURSOS
    ##########################################################################

    cursos = mapa_cursos.get(
        chave,
        []
    )

    if not cursos:

        print(
            f"Sem cursos no CSV: {chave}"
        )

        continue

    ##########################################################################
    # ORGANIZAÇÃO
    ##########################################################################

    for curso in cursos:

        pasta = (
            SAIDA /
            "PorCurso" /
            curso /
            chave[1] /
            disciplina
        )

        pasta.mkdir(
            parents=True,
            exist_ok=True
        )

        shutil.copy2(
            arquivos["plano"],
            pasta / arquivos["plano"].name
        )

        shutil.copy2(
            arquivos["diario"],
            pasta / arquivos["diario"].name
        )

    ##########################################################################
    # RELATÓRIO
    ##########################################################################

    relatorio.append({
        "disciplina": disciplina,
        "codigo": chave[0],
        "periodo": chave[1],
        "turma": chave[2],
        "cursos": ";".join(cursos)
    })

##############################################################################
# EXCEL
##############################################################################

if relatorio:

    df = pd.DataFrame(relatorio)

    with pd.ExcelWriter(
        SAIDA / "relatorio_turmas.xlsx"
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="Geral",
            index=False
        )

        for curso in CURSOS.values():

            curso_df = df[
                df["cursos"].str.contains(
                    curso,
                    na=False
                )
            ]

            curso_df.to_excel(
                writer,
                sheet_name=curso[:31],
                index=False
            )

print("\nOrganização concluída.")