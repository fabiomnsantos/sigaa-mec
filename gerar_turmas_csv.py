from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

import os
import re
import pandas as pd

##############################################################################
# CONFIG
##############################################################################

load_dotenv()

USUARIO = os.getenv("SIGAA_USER")
SENHA = os.getenv("SIGAA_PASS")

PERIODOS = {
    "2023.1",
    "2024.1",
    "2024.2",
    "2025.1",
    "2025.2"
}

SIGAA = "https://sigs.ufrpe.br/sigaa/verTelaLogin.do"

##############################################################################
# EXECUÇÃO
##############################################################################

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    try:

        context = browser.new_context(
            accept_downloads=True,
            ignore_https_errors=True
        )

        page = context.new_page()

        ######################################################################
        # LOGIN
        ######################################################################

        print("Realizando login...")

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

        ######################################################################
        # LISTA DE TURMAS
        ######################################################################

        print("Abrindo lista de turmas...")

        page.goto(
            "https://sigs.ufrpe.br/sigaa/portais/docente/turmas.jsf"
        )

        page.wait_for_load_state(
            "networkidle"
        )

        texto = page.locator(
            "body"
        ).inner_text()

        ######################################################################
        # EXTRAÇÃO
        ######################################################################

        registros = []

        regex = re.compile(
            r"(UAB\d+)\s+(.+?)\s+(\d{4}\.\d)\s+([A-Z0-9]+)\s+\d+",
            re.MULTILINE
        )

        for m in regex.finditer(texto):

            codigo = m.group(1).strip()

            disciplina = (
                m.group(2)
                .strip()
                .replace("\n", " ")
            )

            periodo = m.group(3).strip()

            turma = m.group(4).strip()

            if periodo not in PERIODOS:
                continue

            registros.append({
                "codigo": codigo,
                "disciplina": disciplina,
                "periodo": periodo,
                "turma": turma
            })

        ######################################################################
        # DATAFRAME
        ######################################################################

        df = pd.DataFrame(
            registros
        )

        if df.empty:

            print(
                "Nenhuma turma encontrada."
            )

            raise SystemExit

        df.sort_values(
            ["periodo", "codigo", "turma"],
            inplace=True
        )

        ######################################################################
        # SALVA
        ######################################################################

        df.to_csv(
            "turmas.csv",
            index=False
        )

        ######################################################################
        # RELATÓRIO
        ######################################################################

        print()
        print("=" * 60)
        print("TURMAS ENCONTRADAS")
        print("=" * 60)

        print(df)

        print()
        print(f"Total: {len(df)}")

        print()
        print("Arquivo salvo:")
        print("turmas.csv")

        print("=" * 60)

    finally:

        browser.close()