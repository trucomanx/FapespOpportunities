import os
import json

def verify_default_config(path):
    """
    Cria o arquivo JSON no caminho especificado com conteúdo padrão,
    criando diretórios intermediários se necessário.
    """
    conteudo_padrao = {
        "url": "https://fapesp.br/oportunidades/mais-recentes/",
        "title-contents": ["Bolsa de PD"],
        "body-contents": ["computação", "elétrica", "neural", "neurais", "sinais", "machine learning"]
    }

    # Se o arquivo não existir, cria com o conteúdo padrão
    if not os.path.exists(path):
        # Garante que os diretórios existam
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(conteudo_padrao, f, ensure_ascii=False, indent=4)


# Lê o JSON no início do programa
def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

