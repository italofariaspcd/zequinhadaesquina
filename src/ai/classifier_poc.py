import datetime

def motor_zequinha_v2(user_id, texto_usuario, lat_user, lon_user):
    """
    Versão Evoluída: Classifica e prepara a busca geoespacial.
    """
    # 1. Reutilizamos sua lógica de classificação (IA)
    # (Imagine que a função classificar_demanda_local está aqui)
    categoria_identificada = "PADARIA" # Exemplo fixo para o teste
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 2. Construção da lógica de busca (O que o Engenheiro de Dados precisa)
    pipeline_output = {
        "metadata": {
            "user_id": user_id,
            "timestamp": timestamp,
            "origem": (lat_user, lon_user)
        },
        "processamento": {
            "categoria": categoria_identificada,
            "raio_busca_metros": 2000,
            "query_geo_sugerida": f"SELECT id FROM stores WHERE category='{categoria_identificada}' AND ST_DWithin(geom, ST_MakePoint({lon_user}, {lat_user})::geography, 2000)"
        },
        "acao": f"Disparar Push para lojistas de {categoria_identificada} em Aracaju."
    }
    
    return pipeline_output

# --- TESTANDO O PIPELINE ---
# Simulando um usuário no bairro 13 de Julho, Aracaju
meu_pedido = motor_zequinha_v2(
    user_id="user_123", 
    texto_usuario="Quero pão de sal", 
    lat_user=-10.9255, 
    lon_user=-37.0500
)

import json
print(json.dumps(meu_pedido, indent=4, ensure_ascii=False))