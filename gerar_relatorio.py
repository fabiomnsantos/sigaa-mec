import sys
import tempfile

from pathlib import Path

from pypdf import PdfWriter

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet

##############################################################################
# CONFIGURAÇÃO
##############################################################################

BASE = Path("turmas_passadas_sigaa/PorCurso")
RELATORIOS = Path("Relatorios")

RELATORIOS.mkdir(
    parents=True,
    exist_ok=True
)

##############################################################################
# ARGUMENTOS
##############################################################################

if len(sys.argv) < 2:

    print(
        "\nUso:\n"
        "python gerar_relatorio.py Hidrica\n\n"
        "ou\n\n"
        "python gerar_relatorio.py Hidrica 2024.1 2024.2\n"
    )

    sys.exit()

curso = sys.argv[1]

periodos = sys.argv[2:]

##############################################################################
# LOCALIZA CURSO
##############################################################################

pasta_curso = BASE / curso

if not pasta_curso.exists():

    print(
        f"\nCurso '{curso}' não encontrado.\n"
    )

    sys.exit()

##############################################################################
# COLETA DOS DOCUMENTOS
##############################################################################

planos = []
diarios = []

for periodo_dir in sorted(pasta_curso.iterdir()):

    if not periodo_dir.is_dir():
        continue

    periodo = periodo_dir.name

    if periodos and periodo not in periodos:
        continue

    for disciplina_dir in sorted(periodo_dir.iterdir()):

        if not disciplina_dir.is_dir():
            continue

        for pdf in sorted(
            disciplina_dir.glob("*Plano*.pdf")
        ):

            planos.append(pdf)

        for pdf in sorted(
            disciplina_dir.glob("*diario*.pdf")
        ):

            diarios.append(pdf)

# documentos = []

# for periodo_dir in sorted(pasta_curso.iterdir()):

#     if not periodo_dir.is_dir():
#         continue

#     periodo = periodo_dir.name

#     if periodos and periodo not in periodos:
#         continue

#     for disciplina_dir in sorted(periodo_dir.iterdir()):

#         if not disciplina_dir.is_dir():
#             continue

#         planos = sorted(
#             disciplina_dir.glob("*Plano*.pdf")
#         )

#         diarios = sorted(
#             disciplina_dir.glob("*diario*.pdf")
#         )

#         for pdf in planos:

#             documentos.append({
#                 "periodo": periodo,
#                 "disciplina": disciplina_dir.name,
#                 "tipo": "Plano de Curso",
#                 "arquivo": pdf
#             })

#         for pdf in diarios:

#             documentos.append({
#                 "periodo": periodo,
#                 "disciplina": disciplina_dir.name,
#                 "tipo": "Diário de Turma",
#                 "arquivo": pdf
#             })

# if not documentos:

#     print(
#         "\nNenhum documento encontrado.\n"
#     )

#     sys.exit()

# ##############################################################################
# # CRIA ÍNDICE
# ##############################################################################

# temp_dir = Path(
#     tempfile.mkdtemp()
# )

# indice_pdf = temp_dir / "indice.pdf"

# doc = SimpleDocTemplate(
#     str(indice_pdf)
# )

# styles = getSampleStyleSheet()

# story = []

# # titulo = (
# #     f"Planos de Curso e Diários\n "
# #     f"Curso: {curso}"
# # )

# # story.append(
# #     Paragraph(
# #         titulo,
# #         styles["Title"]
# #     )
# # )

# story.append(
#     Paragraph(
#         "PLANOS DE CURSO E DIÁRIOS DE TURMA",
#         styles["Title"]
#     )
# )

# story.append(
#     Spacer(1, 20)
# )

# story.append(
#     Paragraph(
#         f"<b>Curso:</b> {curso}",
#         styles["Heading2"]
#     )
# )

# story.append(
#     Paragraph(
#         "<b>Docente:</b> Fábio Magalhães de Novaes Santos",
#         styles["Heading2"]
#     )
# )

# story.append(
#     Spacer(1, 20)
# )

# if periodos:

#     story.append(
#         Paragraph(
#             "<b>Períodos:</b> "
#             + ", ".join(periodos),
#             styles["Normal"]
#         )
#     )

# else:

#     story.append(
#         Paragraph(
#             "<b>Períodos:</b> Todos os períodos disponíveis",
#             styles["Normal"]
#         )
#     )

# story.append(
#     Spacer(1, 20)
# )

# story.append(
#     Paragraph(
#         "Documentos incluídos",
#         styles["Heading1"]
#     )
# )

# for i, item in enumerate(documentos, start=1):

#     story.append(
#         Paragraph(
#             (
#                 f"{i}. "
#                 f"{item['periodo']} - "
#                 f"{item['disciplina']} - "
#                 f"{item['tipo']}"
#             ),
#             styles["Normal"]
#         )
#     )

# doc.build(story)

##############################################################################
# PLANOS DE CURSO
##############################################################################

if planos:

    writer = PdfWriter()

    for pdf in planos:

        writer.append(str(pdf))

    if periodos:

        nome = (
            curso
            + "_"
            + "_".join(periodos)
            + "_Planos_de_Curso.pdf"
        )

    else:

        nome = (
            curso
            + "_Planos_de_Curso.pdf"
        )

    saida = RELATORIOS / nome

    with open(saida, "wb") as f:

        writer.write(f)

    writer.close()

    print(
        f"Gerado: {saida}"
    )

##############################################################################
# DIÁRIOS DE TURMA
##############################################################################

if diarios:

    writer = PdfWriter()

    for pdf in diarios:

        writer.append(str(pdf))

    if periodos:

        nome = (
            curso
            + "_"
            + "_".join(periodos)
            + "_Diarios_de_Turma.pdf"
        )

    else:

        nome = (
            curso
            + "_Diarios_de_Turma.pdf"
        )

    saida = RELATORIOS / nome

    with open(saida, "wb") as f:

        writer.write(f)

    writer.close()

    print(
        f"Gerado: {saida}"
    )

##############################################################################
# FIM
##############################################################################

print()
print("=" * 60)
print("RELATÓRIOS GERADOS")
print("=" * 60)
print()