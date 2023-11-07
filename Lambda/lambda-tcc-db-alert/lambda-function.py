import json
import boto3
import pyodbc
import os

def obter_arquivo_mais_recente(nome_bucket, prefixo):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=nome_bucket, Prefix=prefixo)

    objetos = response.get('Contents', [])
    if not objetos:
        raise ValueError("Não há arquivos no bucket com o prefixo especificado.")

    objeto_mais_recente = max(objetos, key=lambda x: x['LastModified'])
    nome_arquivo = objeto_mais_recente['Key']

    obj = s3.get_object(Bucket=nome_bucket, Key=nome_arquivo)
    conteudo_arquivo = obj['Body'].read().decode()
    
    return nome_arquivo, conteudo_arquivo

def parse_conteudo_arquivo(conteudo):
    conteudo = conteudo.replace('\r', '')
    
    linhas = conteudo.strip().split('\n')

    keys = linhas[0].split(';')

    dados = []

    for linha in linhas[1:]:
        valores = linha.split(';')
        dict_dados = {keys[i]: valores[i] for i in range(len(keys))}
        dados.append(dict_dados)
    
    print(dados)
    return dados

def conectar_azure(servidor, banco_dados, usuario, senha):
    conn_str = (
        f"Driver=ODBC Driver 17 for SQL Server;"
        f"Server={servidor};"
        f"Database={banco_dados};"
        f"Uid={usuario};"
        f"Pwd={senha};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=yes;"
        f"Connection Timeout=30;"
    )
    conn = pyodbc.connect(conn_str)
    return conn

def enviar_dados_azure(conn, tabela, dados):
    cursor = conn.cursor()
    
    for dado in dados:
        query = (
            f"INSERT INTO {tabela} (xmin, ymin, xmax, ymax, confidence, class, name, filename)"
            f"VALUES (?, ?, ?, ?, ?, ?, ?, ?);"
        )
        print("envio")
        cursor.execute(query, (dado["xmin"], dado["ymin"], dado["xmax"], dado["ymax"], dado["confidence"], dado["class"], dado["name"], dado["filename"]))
    
    conn.commit()

def lambda_handler(event, context):
    nome_bucket = os.environ.get('BUCKET')
    prefixo = ''
    tabela_azure = os.environ.get('TABELA')
    servidor_azure = os.environ.get('SERVIDOR')
    banco_dados_azure = os.environ.get('BANCO')
    usuario_azure = os.environ.get('USUARIO')
    senha_azure = os.environ.get('SENHA')

    try:
        nome_arquivo, conteudo_arquivo = obter_arquivo_mais_recente(nome_bucket, prefixo)
        dados = parse_conteudo_arquivo(conteudo_arquivo)
        conn = conectar_azure(servidor_azure, banco_dados_azure, usuario_azure, senha_azure)
        enviar_dados_azure(conn, tabela_azure, dados)

        return {
            'statusCode': 200,
            'body': json.dumps('Dados enviados com sucesso para o Azure.')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Erro na execução da função lambda: {str(e)}')
        }
