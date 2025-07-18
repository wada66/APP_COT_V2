from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import date
import psycopg2


def obter_dados_relatorio(protocolo, conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            p.*, 
            r.nome_requerente, r.tipo_de_requerente, r.cpf_cnpj_requerente,
            pr.nome_proprietario, pr.cpf_cnpj_proprietario,
            i.matricula_imovel, i.zona_municipal, i.zona_estadual,
            i.classificacao_diretriz_viaria_metropolitana, i.faixa_servidao,
            i.curva_de_inundacao, i.apa, i.utp, i.manancial,
            i.area, i.localidade_imovel, i.latitude, i.longitude
        FROM processos_2025 p
        LEFT JOIN requerente r ON p.requerente_cpf_cnpj = r.cpf_cnpj_requerente
        LEFT JOIN proprietario pr ON p.proprietario_cpf_cnpj = pr.cpf_cnpj_proprietario
        LEFT JOIN imovel i ON p.matricula_imovel = i.matricula_imovel
        WHERE p.protocolo = %s
    """, (protocolo,))
    row = cur.fetchone()
    colunas = [desc[0] for desc in cur.description]
    return dict(zip(colunas, row)) if row else {}



def gerar_pdf(dados, caminho_pdf):
    c = canvas.Canvas(caminho_pdf, pagesize=A4)
    largura, altura = A4
    x = 2 * cm
    y = altura - 2 * cm
    linha_altura = 18

    def escreve(texto, negrito=False):
        nonlocal y
        if y < 3 * cm:
            c.showPage()
            y = altura - 2 * cm
        if negrito:
            c.setFont("Helvetica-Bold", 11)
        else:
            c.setFont("Helvetica", 10)
        c.drawString(x, y, texto)
        y -= linha_altura

    c.setTitle("Relatório do Processo")
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(largura / 2, y, "Relatório do Processo 2025")
    y -= linha_altura * 2

    escreve(f"Data de geração do relatório: {date.today().strftime('%d/%m/%Y')}")

    escreve("=== Dados do Processo ===", negrito=True)
    escreve(f"Protocolo: {dados.get('protocolo')}")
    escreve(f"Observações: {dados.get('observacoes')}")
    escreve(f"Número da Pasta: {dados.get('numero_pasta')}")
    escreve(f"Solicitação do Requerente: {dados.get('solicitacao_requerente')}")
    escreve(f"Resposta do Departamento: {dados.get('resposta_departamento')}")
    escreve(f"Tramitação: {dados.get('tramitacao')}")
    escreve(f"Setor: {dados.get('setor')}")
    escreve(f"Tipologia: {dados.get('tipologia')}")
    escreve(f"Município: {dados.get('municipio')}")
    escreve(f"Situação da Localização: {dados.get('situacao_localizacao')}")
    escreve(f"Responsável pela Localização: {dados.get('responsavel_localizacao_cpf')}")
    escreve(f"Início da Localização: {dados.get('inicio_localizacao')}")
    escreve(f"Fim da Localização: {dados.get('fim_localizacao')}")
    escreve(f"Dias úteis Localização: {dados.get('dias_uteis_localizacao')}")
    escreve(f"Situação da Análise: {dados.get('situacao_analise')}")
    escreve(f"Responsável pela Análise: {dados.get('responsavel_analise_cpf')}")
    escreve(f"Início da Análise: {dados.get('inicio_analise')}")
    escreve(f"Fim da Análise: {dados.get('fim_analise')}")
    escreve(f"Dias úteis Análise: {dados.get('dias_uteis_analise')}")
    escreve(f"Interesse Social: {'Sim' if dados.get('interesse_social') else 'Não'}")

    escreve("=== Dados do Requerente ===", negrito=True)
    escreve(f"Nome: {dados.get('nome_requerente')}")
    escreve(f"Tipo: {dados.get('tipo_de_requerente')}")
    escreve(f"CPF/CNPJ: {dados.get('cpf_cnpj_requerente')}")

    escreve("=== Dados do Proprietário ===", negrito=True)
    escreve(f"Nome: {dados.get('nome_proprietario')}")
    escreve(f"CPF/CNPJ: {dados.get('cpf_cnpj_proprietario')}")

    escreve("=== Dados do Imóvel ===", negrito=True)
    escreve(f"Matrícula: {dados.get('matricula_imovel')}")
    escreve(f"Zona Estadual: {dados.get('zona_estadual')}")
    escreve(f"Zona Municipal: {dados.get('zona_municipal')}")
    escreve(f"Classificação Diretriz Viária: {dados.get('classificacao_diretriz')}")
    escreve(f"Faixa de Servidão: {dados.get('faixa_servidao')}")
    escreve(f"Curva de Inundação: {dados.get('curva_de_inundacao')}")
    escreve(f"APA: {dados.get('apa')}")
    escreve(f"UTP: {dados.get('utp')}")
    escreve(f"Manancial: {dados.get('manancial')}")
    escreve(f"Área: {dados.get('area')} m²")
    escreve(f"Latitude: {dados.get('latitude')}")
    escreve(f"Longitude: {dados.get('longitude')}")
    escreve(f"Localidade: {dados.get('localidade_imovel')}")
    escreve(f"Lei Inclui Perímetro Urbano: {'Sim' if dados.get('lei_inclui_perimetro_urbano') else 'Não'}")

    escreve("=== Nome/Loteamento ===", negrito=True)
    escreve(f"Nome ou loteamento do condomínio a ser aprovado:")
    escreve(dados.get("nome_ou_loteamento_do_condominio_a_ser_aprovado", "") or "Não informado")

    c.save()

def gerar_pdf_requerente(dados, caminho_pdf):
    c = canvas.Canvas(caminho_pdf, pagesize=A4)
    largura, altura = A4
    x = 2 * cm
    y = altura - 2 * cm
    linha_altura = 18

    def escreve(texto, negrito=False):
        nonlocal y
        if y < 3 * cm:
            c.showPage()
            y = altura - 2 * cm
        c.setFont("Helvetica-Bold" if negrito else "Helvetica", 10)
        c.drawString(x, y, texto)
        y -= linha_altura

    c.setTitle("Relatório do Requerente")
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(largura / 2, y, "Relatório do Requerente")
    y -= linha_altura * 2

    escreve(f"Data de geração do relatório: {date.today().strftime('%d/%m/%Y')}")

    escreve("=== Dados Preenchidos ===", negrito=True)

    for chave, valor in dados.items():
        if valor not in [None, "", False]:
            texto = f"{chave.replace('_', ' ').capitalize()}: {valor}"
            escreve(texto)

    c.save()