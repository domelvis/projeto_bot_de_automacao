# -*- coding: utf-8 -*-
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

def conectar_banco():
    try:
        conexao = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'bot_automacao'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '8531'),
            client_encoding='UTF8'
        )
        print("✅ Conexão com PostgreSQL estabelecida com sucesso!")
        return conexao
    except psycopg2.OperationalError as e:
        print(f"❌ Erro operacional: {e}")
        return None
    except psycopg2.Error as e:
        print(f"❌ Erro no PostgreSQL: {e}")
        return None
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return None

def testar_conexao():
    """Testa a conexão e exibe informações do banco"""
    conn = conectar_banco()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            versao = cursor.fetchone()
            print(f"📊 Versão do PostgreSQL: {versao[0]}")

            cursor.execute("SHOW server_encoding;")
            encoding = cursor.fetchone()
            print(f"🔤 Codificação do servidor: {encoding[0]}")

            cursor.close()
            conn.close()
            print("🔐 Conexão fechada com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao testar conexão: {e}")
    else:
        print("❌ Não foi possível conectar ao banco de dados")

# Funções CRUD

def inserir_dado(tabela, dados):
    """Insere um registro na tabela"""
    conn = conectar_banco()
    if conn:
        try:
            cursor = conn.cursor()
            cols = ', '.join(dados.keys())
            vals = ', '.join(['%s'] * len(dados))
            query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(tabela),
                sql.SQL(cols),
                sql.SQL(vals)
            )
            cursor.execute(query, list(dados.values()))
            conn.commit()
            print(f"✅ Dados inseridos em {tabela}")
            cursor.close()
        except Exception as e:
            print(f"❌ Erro ao inserir dado: {e}")
        finally:
            conn.close()

def consultar_dados(tabela, colunas='*', where=None):
    """Consulta registros da tabela"""
    conn = conectar_banco()
    resultados = []
    if conn:
        try:
            cursor = conn.cursor()
            query = f"SELECT {colunas} FROM {tabela}"
            if where:
                query += f" WHERE {where}"
            cursor.execute(query)
            resultados = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"❌ Erro ao consultar dados: {e}")
        finally:
            conn.close()
    return resultados

def atualizar_dado(tabela, dados, where):
    """Atualiza registros da tabela"""
    conn = conectar_banco()
    if conn:
        try:
            cursor = conn.cursor()
            set_expr = ', '.join([f"{k}=%s" for k in dados.keys()])
            query = f"UPDATE {tabela} SET {set_expr} WHERE {where}"
            cursor.execute(query, list(dados.values()))
            conn.commit()
            print(f"✅ Dados atualizados em {tabela}")
            cursor.close()
        except Exception as e:
            print(f"❌ Erro ao atualizar dados: {e}")
        finally:
            conn.close()

def deletar_dado(tabela, where):
    """Deleta registros da tabela"""
    conn = conectar_banco()
    if conn:
        try:
            cursor = conn.cursor()
            query = f"DELETE FROM {tabela} WHERE {where}"
            cursor.execute(query)
            conn.commit()
            print(f"✅ Dados deletados de {tabela}")
            cursor.close()
        except Exception as e:
            print(f"❌ Erro ao deletar dados: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    print("🔄 Testando conexão com PostgreSQL...")
    testar_conexao()

    # Exemplos rápidos de CRUD
    # inserir_dado('sua_tabela', {'col1':'valor1', 'col2':'valor2'})
    # print(consultar_dados('sua_tabela'))
    # atualizar_dado('sua_tabela', {'col1':'novo_valor'}, "col2='valor2'")
    # deletar_dado('sua_tabela', "col1='novo_valor'")
