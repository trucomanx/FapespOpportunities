import os
import json

DEFAULT_CONTENT = {
    "url": "https://fapesp.br/oportunidades/mais-recentes/",
    "title-contents": ["Bolsa de PD", "Bolsas de PD"],
    "title-contents-filters": ["neurais","visão"],
    "body-contents": ["neurais","visão","computação", "elétrica", "neural",  "sinais", "machine learning"],
    "avoid_ids":[]
}

def verify_default_config(path):
    """
    Garante que o arquivo JSON exista com todas as chaves de DEFAULT_CONTENT.
    Se o arquivo não existir, cria com o conteúdo padrão.
    Se faltar alguma chave, adiciona com o valor padrão e sobrescreve o arquivo.
    """

    config_data = {}

    # Se o arquivo existir, carrega o conteúdo
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            try:
                config_data = json.load(f)
            except json.JSONDecodeError:
                # Se o JSON estiver corrompido, cria um novo
                config_data = {}
    else:
        # Garante que os diretórios existam
        os.makedirs(os.path.dirname(path), exist_ok=True)

    # Verifica se todas as chaves de DEFAULT_CONTENT estão presentes
    updated = False
    for key, value in DEFAULT_CONTENT.items():
        if key not in config_data:
            config_data[key] = value
            updated = True

    # Se o arquivo não existia ou se alguma chave foi adicionada, salva o arquivo
    if not os.path.exists(path) or updated:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)



# Lê o JSON no início do programa
def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config_path,config_data):
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)
