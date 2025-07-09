from flask import Flask, render_template, request, redirect
import psycopg2
from psycopg2 import sql
from datetime import date
import os
from dotenv import load_dotenv
from datetime import date, timedelta, datetime

import numpy as np

def calcular_dias_uteis(inicio_str, fim_str):
    if not inicio_str or not fim_str:
        return None
    try:
        inicio = datetime.strptime(inicio_str, "%Y-%m-%d").date()
        fim = datetime.strptime(fim_str, "%Y-%m-%d").date()
        return int(np.busday_count(inicio, fim))  # conta dias úteis entre datas
    except Exception as e:
        print("Erro ao calcular dias úteis:", e)
        return None


app = Flask(__name__)




# Carregar variáveis do .env
load_dotenv()

# Acessar variáveis
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Configurar sua conexão com o banco PostgreSQL
conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

def carregar_enum(nome_enum):
    cur = conn.cursor()
    cur.execute(sql.SQL("SELECT unnest(enum_range(NULL::{}))").format(sql.Identifier(nome_enum)))
    valores = [row[0] for row in cur.fetchall()]
    cur.close()
    return valores

@app.route("/")
def index():
    cur = conn.cursor()

    cur.execute("SELECT nome_setor FROM setor")
    setores = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT nome_municipio FROM municipios")
    municipios = [row[0] for row in cur.fetchall()]

    enums = {
        "classificacao_diretriz_viaria": carregar_enum("tipo_classificacao_diretriz_viaria"),
        "faixa_servidao": carregar_enum("tipo_faixa_servidao"),
        "curva_de_inundacao": carregar_enum("tipo_curva_de_inundacao"),
        "apa": carregar_enum("tipo_apa"),
        "utp": carregar_enum("tipo_utp"),
        "manancial": carregar_enum("tipo_manancial")
    }

    solicitacoes_respostas = [
        'ANUÊNCIA PRÉVIA', 'CONSULTA PRÉVIA', 'DESPACHO',
        'INFORMAÇÃO', 'PARECER', 'REVALIDAÇÃO'
    ]
    tramitacoes = [
        'ANÁLISE', 'ARQUIVADO', 'DEVOLVIDO', 'ENCAMINHADO EXT', 'ENCAMINHADO INT',
        'LOCALIZAÇÃO', 'RETORNOU P/ ANÁLISE', 'RETORNOU PRA LOCALIZAÇÃO',
        'SOBRESTADO 01', 'SOBRESTADO 02', 'SOBRESTADO 03',
        'SOBRESTADO 04', 'SOBRESTADO 05', '(P/ASSINAR)', '*PRIORIDADE*'
    ]
    tipologias = [
        'CONDOMÍNIO EDILÍCIO', 'CONDOMÍNIO DE LOTES', 'CURVA DE INUNDAÇÃO',
        'DESAFETAÇÃO/AFETAÇÃO', 'DESMEMBRAMENTO', 'DIRETRIZ VIÁRIA',
        'LOTEAMENTO', 'MANANCIAL', 'OUTROS', 'REURB',
        'USO DO SOLO', 'ZONEAMENTO', '(MP - AÇÃO JUDICIAL)'
    ]
    situacoes_localizacao = ['LOCALIZADA', 'NÃO PRECISA LOCALIZAR']
    situacoes_analise = ['FINALIZADA', 'NÃO FINALIZADA']

    cur.execute("SELECT cpf_servidor, nome_servidor FROM servidor")
    servidores = cur.fetchall()

    cur.close()
    return render_template("formulario.html",
                           setores=setores,
                           municipios=municipios,
                           enums=enums,
                           solicitacoes_respostas=solicitacoes_respostas,
                           tramitacoes=tramitacoes,
                           tipologias=tipologias,
                           situacoes_localizacao=situacoes_localizacao,
                           situacoes_analise=situacoes_analise,
                           servidores=servidores)

@app.route("/inserir", methods=["POST"])
def inserir():
    cur = conn.cursor()
    
    from datetime import date, timedelta

    # Datas automáticas
    data_entrada = date.today()
    data_previsao_resposta = data_entrada + timedelta(days=40)


    # Dados do processo
    protocolo = request.form.get("protocolo")
    observacoes = request.form.get("observacoes")
    numero_pasta = request.form.get("numero_pasta") or None
    solicitacao_requerente = request.form.get("solicitacao_requerente")
    resposta_departamento = request.form.get("resposta_departamento")
    tramitacao = request.form.get("tramitacao")
    setor = request.form.get("setor")
    tipologia = request.form.get("tipologia")
    municipio = request.form.get("municipio")
    situacao_localizacao = request.form.get("situacao_localizacao")
    responsavel_localizacao_cpf = request.form.get("responsavel_localizacao_cpf") or None
    inicio_localizacao = request.form.get("inicio_localizacao") or None
    fim_localizacao = request.form.get("fim_localizacao") or None
    situacao_analise = request.form.get("situacao_analise")
    responsavel_analise_cpf = request.form.get("responsavel_analise_cpf") or None
    inicio_analise = request.form.get("inicio_analise") or None
    fim_analise = request.form.get("fim_analise") or None
    dias_uteis_analise = request.form.get("dias_uteis_analise")
    dias_uteis_localizacao = request.form.get("dias_uteis_localizacao")
    requerente_cpf_cnpj = request.form.get("cpf_cnpj_requerente") or None
    proprietario_cpf_cnpj = request.form.get("cpf_cnpj_proprietario") or None
    nome_ou_loteamento_do_condominio = request.form.get("nome_ou_loteamento_do_condominio_a_ser_aprovado")
    interesse_social = request.form.get("interesse_social") == "on"
    lei_inclui_perimetro_urbano = request.form.get("lei_inclui_perimetro_urbano") == "on"


    
        # Cálculo de dias úteis
    dias_uteis_localizacao = calcular_dias_uteis(inicio_localizacao, fim_localizacao)
    dias_uteis_analise = calcular_dias_uteis(inicio_analise, fim_analise)

    # Dados do imóvel
    matricula_imovel = request.form.get("matricula_imovel") or None
    zona_estadual = request.form.get("zona_estadual") or None
    zona_municipal = request.form.get("zona_municipal") or None
    classificacao_diretriz = request.form.get("classificacao_diretriz") or None
    faixa_servidao = request.form.get("faixa_servidao") or None
    curva_de_inundacao = request.form.get("curva_de_inundacao") or None
    apa = request.form.get("apa") or None
    utp = request.form.get("utp") or None
    manancial = request.form.get("manancial") or None
    area = request.form.get("area")
    localidade_imovel = request.form.get("localidade_imovel")
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")

    # Dados do requerente
    nome_requerente = request.form.get("nome_requerente")
    tipo_de_requerente = request.form.get("tipo_de_requerente")

    # Dados do proprietário
    nome_proprietario = request.form.get("nome_proprietario")

    # Inserir requerente (se informado)
    if requerente_cpf_cnpj and nome_requerente and tipo_de_requerente:
        try:
            cur.execute("""
                INSERT INTO requerente (cpf_cnpj_requerente, nome_requerente, tipo_de_requerente)
                VALUES (%s, %s, %s)
                ON CONFLICT (cpf_cnpj_requerente) DO NOTHING
            """, (requerente_cpf_cnpj, nome_requerente, tipo_de_requerente))
        except Exception as e:
            print("Erro ao inserir requerente:", e)

    # Inserir proprietário (se informado)
    if proprietario_cpf_cnpj and nome_proprietario:
        try:
            cur.execute("""
                INSERT INTO proprietario (cpf_cnpj_proprietario, nome_proprietario)
                VALUES (%s, %s)
                ON CONFLICT (cpf_cnpj_proprietario) DO NOTHING
            """, (proprietario_cpf_cnpj, nome_proprietario))
        except Exception as e:
            print("Erro ao inserir proprietario:", e)

    # Inserir imóvel (se informado)
    if matricula_imovel:
        try:
            cur.execute("""
            INSERT INTO imovel (
             matricula_imovel, zona_municipal, zona_estadual, classificacao_diretriz_viaria_metropolitana,
            faixa_servidao, curva_de_inundacao, apa, utp, manancial, area,
            localidade_imovel, latitude, longitude, lei_inclui_perimetro_urbano
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (matricula_imovel) DO NOTHING
            """, (
    matricula_imovel, zona_municipal, zona_estadual, classificacao_diretriz,
    faixa_servidao, curva_de_inundacao, apa, utp, manancial,
    float(area) if area else None, localidade_imovel,
    float(latitude) if latitude else None, float(longitude) if longitude else None,
    lei_inclui_perimetro_urbano
))

        except Exception as e:
            print("Erro ao inserir imovel:", e)

    # Inserir relação proprietario_imovel (se proprietario e imovel informados)
    if proprietario_cpf_cnpj and matricula_imovel:
        try:
            cur.execute("""
                INSERT INTO proprietario_imovel (cpf_cnpj_proprietario, matricula_imovel)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (proprietario_cpf_cnpj, matricula_imovel))
        except Exception as e:
            print("Erro ao inserir proprietario_imovel:", e)

    # ✅ Inserir número da pasta (para evitar erro de chave estrangeira)
    if numero_pasta:
        try:
            cur.execute("""
                INSERT INTO pasta (numero_pasta)
                VALUES (%s)
                ON CONFLICT (numero_pasta) DO NOTHING
            """, (numero_pasta,))
        except Exception as e:
            print("Erro ao inserir pasta:", e)

    # Inserir processo 2025
    try:
        cur.execute("""
        INSERT INTO processos_2025 (
        protocolo, observacoes, matricula_imovel, numero_pasta, solicitacao_requerente,
        resposta_departamento, tramitacao, setor, tipologia, municipio, situacao_localizacao,
        responsavel_localizacao_cpf, inicio_localizacao, fim_localizacao, situacao_analise,
        responsavel_analise_cpf, inicio_analise, fim_analise, dias_uteis_analise,
        dias_uteis_localizacao, requerente_cpf_cnpj, proprietario_cpf_cnpj,
        nome_ou_loteamento_do_condominio_a_ser_aprovado, interesse_social,
        data_entrada, data_previsao_resposta
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

            """, (
        protocolo, observacoes, matricula_imovel, numero_pasta, solicitacao_requerente,
        resposta_departamento, tramitacao, setor, tipologia, municipio, situacao_localizacao,
        responsavel_localizacao_cpf, inicio_localizacao, fim_localizacao, situacao_analise,
        responsavel_analise_cpf, inicio_analise, fim_analise,
        dias_uteis_analise, dias_uteis_localizacao,
        requerente_cpf_cnpj, proprietario_cpf_cnpj, nome_ou_loteamento_do_condominio,
        interesse_social, data_entrada, data_previsao_resposta
    ))

        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Erro ao inserir processo:", e)
        return f"Erro ao inserir processo: {e}", 500

    cur.close()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
