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
    try:
        data = json.loads(conteudo)
    except json.JSONDecodeError:
        raise ValueError("Conteúdo do arquivo não é um JSON válido.")

    if not isinstance(data, list):
        raise ValueError("Conteúdo do arquivo não está no formato esperado.")

    emotions_data = []
    for entry in data:
        emotions = entry.get("Emotions", [])
        for emotion in emotions:
            emotions_data.append({
                "filename": entry.get("Filename"),
                "emotionType": emotion.get("Type"),
                "emotionConfidence": emotion.get("Confidence")
            })

    return emotions_data

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
            f"INSERT INTO {tabela} (filename, emotionType, emotionConfidence) "
            f"VALUES (?, ?, ?);"
        )
        cursor.execute(query, (dado["filename"], dado["emotionType"], dado["emotionConfidence"]))

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
