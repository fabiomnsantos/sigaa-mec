import re
import pandas as pd

from pathlib import Path

##############################################################################
# CONFIGURAÇÃO
##############################################################################

PASTA = Path("downloads_sigaa")

##############################################################################
# IDENTIFICAÇÃO
##############################################################################

def extrair_chave(nome):

    m = re.search(
        r"(UAB\d+)_(\d+\.\d)_(\d+)",
        nome,
        re.IGNORECASE
    )

    if not m:
        return None

    return (
        m.group(1),
        m.group(2),
        m.group(3)
    )


def identificar_tipo(nome):

    nome = nome.lower()

    if "plano" in nome:
        return "plano"

    if "diario" in nome:
        return "diario"

    if (
        "discente" in nome
        or "discentes" in nome
        or "participante" in nome
        or "participantes" in nome
    ):
        return "discentes"

    return None

##############################################################################
# VARREDURA
##############################################################################

turmas = {}

for pdf in PASTA.glob("*.pdf"):

    chave = extrair_chave(pdf.name)

    if chave is None:
        continue

    tipo = identificar_tipo(pdf.name)

    if tipo is None:
        continue

    if chave not in turmas:

        turmas[chave] = {
            "plano": False,
            "diario": False,
            "discentes": False
        }

    turmas[chave][tipo] = True

##############################################################################
# RELATÓRIO
##############################################################################

linhas = []

faltando_plano = 0
faltando_diario = 0
faltando_discentes = 0

for chave, docs in sorted(turmas.items()):

    codigo, periodo, turma = chave

    status = "OK"

    faltas = []

    if not docs["plano"]:
        faltando_plano += 1
        faltas.append("Plano")

    if not docs["diario"]:
        faltando_diario += 1
        faltas.append("Diário")

    if not docs["discentes"]:
        faltando_discentes += 1
        faltas.append("Discentes")

    if faltas:
        status = "FALTANDO"

    linhas.append({
        "codigo": codigo,
        "periodo": periodo,
        "turma": turma,
        "plano": docs["plano"],
        "diario": docs["diario"],
        "discentes": docs["discentes"],
        "status": status,
        "faltando": ", ".join(faltas)
    })

##############################################################################
# DATAFRAME
##############################################################################

df = pd.DataFrame(linhas)

arquivo_excel = PASTA / "verificacao_downloads.xlsx"

with pd.ExcelWriter(arquivo_excel) as writer:

    df.to_excel(
        writer,
        sheet_name="Turmas",
        index=False
    )

##############################################################################
# RESUMO
##############################################################################

print()
print("=" * 60)
print("RESUMO")
print("=" * 60)

print(f"Turmas encontradas: {len(df)}")

print()

print(f"Planos faltando:     {faltando_plano}")
print(f"Diários faltando:    {faltando_diario}")
print(f"Discentes faltando:  {faltando_discentes}")

print()

if (
    faltando_plano == 0
    and faltando_diario == 0
    and faltando_discentes == 0
):
    print("✓ Todas as turmas estão completas.")

else:
    print("⚠ Existem documentos faltando.")

print()
print("Relatório:")
print(arquivo_excel)
print("=" * 60)