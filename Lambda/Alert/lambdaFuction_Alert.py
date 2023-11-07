import json
import os
import requests
import boto3

import boto3

def obter_arquivo_mais_recente(nome_s3, nome_bucket):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=nome_bucket)
    objetos = response['Contents']
    objetos_ordenados = sorted(objetos, key=lambda x: x['LastModified'], reverse=True)
    nome_arquivo_mais_recente = objetos_ordenados[0]['Key']
    obj = s3.get_object(Bucket=nome_bucket, Key=nome_arquivo_mais_recente)
    body = obj['Body'].read().decode()
    return nome_arquivo_mais_recente, body



def porcentagem(conteudo_arquivo):
    linhas = conteudo_arquivo.strip().split('\n')
    soma_confidence = 0.0
    soma_confidence_gun = 0.0

    for linha in linhas[1:]:  # Começando do índice 1 para ignorar o cabeçalho
        valores = linha.split(';')  # Usar ';' como separador
        if len(valores) >= 5:  # Verificar se a linha tem pelo menos 5 colunas (a coluna do confidence)
            confidence_str = valores[4]
            name = valores[6].lower()  # Convertendo para minúsculas
            
            try:
                confidence = round(float(confidence_str) * 100) / 100
                print(f"Valor lido e convertido: {confidence:.2f}")
                
                if name == 'gun':
                    print(f"Nome da classe: {name}")
                    print(f"Valor de confidence 'gun' antes da adição de 10: {confidence_str}")
                    confidence_gun = float(confidence_str) *2
                    print(f"Valor de confidence 'gun' após a adição de 10: {confidence_gun}")
                    soma_confidence_gun += confidence_gun
                else:
                    soma_confidence += confidence
                
            except ValueError:
                print(f"Não foi possível converter o valor de confidence: {confidence_str}")

    print(f"Resultado da soma (confiança normal): {soma_confidence:.2f}")
    print(f"Resultado da soma (confiança gun): {soma_confidence_gun:.2f}")
    
    somafinal = (soma_confidence + soma_confidence_gun) * 100 / 4
    return round(somafinal , 2 )  # Arredondar a soma com duas casas decimais 



def last_chat_id(token):
    try:
        url = "https://api.telegram.org/bot{}/getUpdates".format(token)
        response = requests.get(url)
        if response.status_code == 200:
            json_msg = response.json()
            for json_result in reversed(json_msg['result']):
                message_keys = json_result['message'].keys()
                if ('chat' in message_keys) or ('group_chat_created' in message_keys):
                    return json_result['message']['chat']['id']
            print('Nenhum grupo encontrado')
        else:
            print('A resposta falhou, código de status: {}'.format(response.status_code))
    except Exception as e:
        print("Erro no getUpdates:", e)


def send_message(token, chat_id, message):
    try:
        data = {"chat_id": chat_id, "text": message}
        url = "https://api.telegram.org/bot{}/sendMessage".format(token)
        requests.post(url, data)
    except Exception as e:
        print("Erro no sendMessage:", e)


def mover_arquivo(nome_s3, nome_bucket_origem, nome_bucket_destino):
    s3 = boto3.client('s3')
  
    nome_arquivo, conteudo_arquivo = obter_arquivo_mais_recente(nome_s3, nome_bucket_origem)

    s3.copy_object(
        Bucket=nome_bucket_destino,
        CopySource={'Bucket': nome_bucket_origem, 'Key': nome_arquivo},
        Key=nome_arquivo
    )

    s3.delete_object(
        Bucket=nome_bucket_origem,
        Key=nome_arquivo
    )

    return nome_arquivo, conteudo_arquivo


def lambda_handler(event, context):
    
    # Configurações
    nome_s3 = "s3-data-tcc-processed"
    nome_bucket_origem = "s3-data-tcc-processed"
    nome_bucket_destino = "s3-data-tcc-processed-alert"
    token = os.environ.get('TOKEN')

    try:
        nome_arquivo, conteudo_arquivo = mover_arquivo(nome_s3, nome_bucket_origem, nome_bucket_destino)
        print(conteudo_arquivo)

        chat_id = last_chat_id(token)
        print("Id do chat:", chat_id)

        alerta_assalto = porcentagem(conteudo_arquivo)
        mensagem = "⚠!!!CUIDADO!!!⚠\nALERTA DE ASSALTO COM {}% DE CHANCE".format(alerta_assalto)

        send_message(token, chat_id, mensagem)

        return {
            'statusCode': 200,
            'body': json.dumps('Mensagem enviada e arquivo movido com sucesso.')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Erro na execução da função lambda: {str(e)}')
        }

