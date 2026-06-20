from playwright.sync_api import sync_playwright
from pathlib import Path
from dotenv import load_dotenv

import pandas as pd
import os

##############################################################################
# CONFIG
##############################################################################

load_dotenv()

USUARIO = os.getenv("SIGAA_USER")
SENHA = os.getenv("SIGAA_PASS")

DOWNLOADS = Path("downloads_sigaa")
DOWNLOADS.mkdir(exist_ok=True)

SIGAA = "https://sigs.ufrpe.br/sigaa/verTelaLogin.do"

##############################################################################
# FUNÇÕES
##############################################################################

def abrir_turma(page, codigo, periodo, turma):

    linhas = page.locator("tr")

    for i in range(linhas.count()):

        try:

            linha = linhas.nth(i)

            tds = linha.locator("td")

            if tds.count() < 4:
                continue

            codigo_linha = (
                tds.nth(0)
                .inner_text()
                .strip()
            )

            periodo_linha = (
                tds.nth(2)
                .inner_text()
                .strip()
            )

            turma_linha = (
                tds.nth(3)
                .inner_text()
                .strip()
            )

            if (
                codigo_linha == codigo
                and periodo_linha == periodo
                and turma_linha == turma
            ):

                tds.nth(1).locator("a").click()

                page.wait_for_load_state("networkidle")

                return True

        except:
            pass

    return False


def extrair_cursos(page):

    print("Abrindo participantes...")

    page.evaluate("""
    () => {

        const links =
            [...document.querySelectorAll('a')];

        const alvo = links.find(
            a =>
            a.textContent.trim() ===
            'Participantes'
        );

        if(alvo){
            alvo.click();
        }

    }
    """)

    page.wait_for_timeout(4000)

    texto = page.locator(
        "body"
    ).inner_text().upper()

    cursos = []

    if "ENGENHARIA DA COMPUTAÇÃO" in texto:
        cursos.append("Computacao")

    if "ENGENHARIA DE CONTROLE" in texto:
        cursos.append("Controle")

    if "ENGENHARIA QUÍMICA" in texto:
        cursos.append("Quimica")

    if "ENGENHARIA HÍDRICA" in texto:
        cursos.append("Hidrica")

    return cursos

##############################################################################
# EXECUÇÃO
##############################################################################

turmas = pd.read_csv(
    "turmas.csv",
    dtype=str
)

#turmas = turmas.head(1) # teste temporário

relatorio = []

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    context = browser.new_context(
        accept_downloads=True,
        ignore_https_errors=True
    )

    page = context.new_page()

    ##########################################################################
    # LOGIN
    ##########################################################################

    page.goto(
        SIGAA,
        wait_until="domcontentloaded"
    )

    page.locator(
        'input[name="user.login"]'
    ).fill(USUARIO)

    page.locator(
        'input[name="user.senha"]'
    ).fill(SENHA)

    page.locator(
        'input[type="submit"]'
    ).click()

    page.wait_for_load_state(
        "networkidle"
    )

    try:

        page.get_by_role(
            "button",
            name="Ciente"
        ).click(timeout=1000)

        print("Cookies aceitos.")

    except:

        pass

    print()
    print("=" * 60)
    print("LOGIN REALIZADO")
    print("=" * 60)

    ##########################################################################
    # LOOP
    ##########################################################################

    for _, linha in turmas.iterrows():

        try:

            codigo = linha["codigo"]

            disciplina = linha["disciplina"]

            periodo = linha["periodo"]

            turma = str(
                linha["turma"]
            ).zfill(2)

            print()
            print(
                f"Processando: "
                f"{codigo} "
                f"{periodo} "
                f"T{turma}"
            )

            ######################################################################
            # VOLTA PARA LISTA
            ######################################################################

            page.goto(
                "https://sigs.ufrpe.br/sigaa/portais/docente/turmas.jsf"
            )

            page.wait_for_load_state(
                "networkidle"
            )

            ######################################################################
            # ABRE TURMA
            ######################################################################

            ok = abrir_turma(
                page,
                codigo,
                periodo,
                turma
            )

            if not ok:

                print(
                    "Turma não encontrada."
                )

                continue

            ######################################################################
            # DIÁRIO
            ######################################################################

            nome = (
                f"diario_{codigo}_"
                f"{periodo}_{turma}_.pdf"
            )

            arquivo_diario = (
                DOWNLOADS / nome
            )

            if not arquivo_diario.exists():

                with page.expect_download() as d:

                    page.evaluate("""
                    () => {

                        const itens =
                            [...document.querySelectorAll('.itemMenu')];

                        const diario =
                            itens.find(
                                el =>
                                el.textContent.trim() ===
                                'Diário de Turma'
                            );

                        if(diario){
                            diario.click();
                        }

                    }
                    """)

                download = d.value

                download.save_as(
                    arquivo_diario
                )

                print(
                    f"Baixado: {nome}"
                )

            else:

                print(
                    f"Já existe: {nome}"
                )
            

            ######################################################################
            # PLANO
            ######################################################################

            arquivo_plano = (
                DOWNLOADS /
                f"Plano_de_Curso_{codigo}_{periodo}_{turma}_.pdf"
            )

            if not arquivo_plano.exists():

                with page.expect_download() as d:

                    page.evaluate("""
                    () => {

                        const itens =
                            [...document.querySelectorAll('.itemMenu')];

                        const plano =
                            itens.find(
                                el =>
                                el.textContent.trim() ===
                                'Imprimir Plano de Curso'
                            );

                        if(plano){
                            plano.click();
                        }

                    }
                    """)

                download = d.value

                download.save_as(
                    arquivo_plano
                )

                print(
                    f"Baixado: {arquivo_plano.name}"
                )

            else:

                print(
                    f"Já existe: {arquivo_plano.name}"
                )

            ja_processada = (
                arquivo_diario.exists()
                and arquivo_plano.exists()
            )

            if ja_processada:

                print(
                    f"Turma já processada: "
                    f"{codigo} {periodo} T{turma}"
                )

                continue

            ######################################################################
            # CURSOS
            ######################################################################

            cursos = extrair_cursos(
                page
            )

            relatorio.append({
                "codigo": codigo,
                "disciplina": disciplina,
                "periodo": periodo,
                "turma": turma,
                "cursos": ";".join(cursos)
            })

            print(
                "Cursos:",
                cursos
            )

            ##############################################################################
            # CSV MESTRE
            ##############################################################################

            df = pd.DataFrame(
                relatorio
            ).to_csv(
                DOWNLOADS /
                "turmas_mestre.csv",
                index=False
            )

            print(
                f"OK: {codigo} {periodo} T{turma}"
            )
            
        except Exception as e:

            print()

            print(
                f"ERRO: {codigo} {periodo} T{turma}"
            )

            print(e)

            continue
    ##########################################################################
    # FIM DO LOOP
    ##########################################################################

    browser.close()

##############################################################################
# FINAL
##############################################################################

print()
print("=" * 60)
print("CONCLUÍDO")
print("=" * 60)
print()

print(
    DOWNLOADS /
    "turmas_mestre.csv"
)