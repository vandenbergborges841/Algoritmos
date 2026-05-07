"""
Algoritmo de Simulação de Interferência WLAN e Bloqueio de Canais de Sensores
------------------------------------------------------------------------------
Inspirado no processo de avaliação ilustrado na figura image_0.png, cenários 'a' a 'e'.
Este script estima a interferência WLAN em canais de sensores e determina o bloqueio.
"""

def estimar_interferencia_wlan(cenario_id, canais_sensores, canais_wlan, limiar_bloqueio):
    """
    Executa a simulação para um cenário específico.
    """
    print(f"\n--- Processando Cenário: {cenario_id.upper()} ---")
    
    # Mapeamento de cores da figura para valores de potência de interferência estimada (dBr)
    # A interferência diminui conforme o canal se afasta do centro da WLAN.
    potencias_por_distancia = {
        0: 0,      # Canal central da WLAN, interferência máxima
        1: -40,    # 1 canal de distância, atenuação de -40 dBr
        2: -34,    # 2 canais de distância, atenuação de -34 dBr
        3: -24,    # 3 canais de distância, atenuação de -24 dBr
        4: -20     # 4 canais de distância, atenuação de -20 dBr
    }

    # Estrutura para armazenar o resultado final de cada canal de sensor
    estado_canais = {ch: {"estado": "Ativo", "potencia_interf_dBr": None, "cor_estado": "Verde (Ativo)"} 
                     for ch in canais_sensores}

    # 1. Identificar canais de sensores sobrepostos pela WLAN
    # Para simplificar, assumimos que canais de sensores listados nos canais WLAN estão sobrepostos.
    canais_sobrepostos = [ch for ch in canais_sensores if ch in canais_wlan]

    # Encontrar o(s) canal(is) central(is) da WLAN para referência de distância
    min_wlan_ch = min(canais_wlan)
    max_wlan_ch = max(canais_wlan)
    centros_wlan = list(range(int((min_wlan_ch + max_wlan_ch)/2), int((min_wlan_ch + max_wlan_ch)/2) + 2))

    print(f"Canais de Sensores: {list(canais_sensores)}")
    print(f"Canais WLAN (Interferência): {list(canais_wlan)}")
    print(f"Canais sobrepostos identificados: {canais_sobrepostos}")

    # 2. Avaliar cada canal de sensor
    for sensor_ch in canais_sensores:
        # Se não há sobreposição, o canal permanece ativo e com interferência nula/não estimada.
        if sensor_ch not in canais_sobrepostos:
            continue

        # 3. Calcular a potência de interferência para o canal sobreposto
        # Baseado na distância mínima para qualquer canal central da WLAN.
        distancia = min(abs(sensor_ch - centro) for centro in centros_wlan)
        
        # Mapeia a distância para a potência de interferência de acordo com a figura
        interferencia_estimada = potencias_por_distancia.get(distancia, -20) # Valor mínimo de atenuação se muito longe

        # 4. Decisão de Bloqueio
        # Se a interferência for maior ou igual ao limiar de bloqueio do cenário, o canal é bloqueado.
        if interferencia_estimada >= limiar_bloqueio:
            estado_canais[sensor_ch]["estado"] = "BLOQUEADO"
            # Determina a cor com base na potência da interferência
            if interferencia_estimada == 0:
                estado_canais[sensor_ch]["cor_estado"] = "Laranja (Ativo)" # Como no cenário C
            elif interferencia_estimada == -34:
                estado_canais[sensor_ch]["cor_estado"] = "Amarelo (Primeiro bloqueado)"
            elif interferencia_estimada == -24:
                estado_canais[sensor_ch]["cor_estado"] = "Amarelo Escuro (Segundo bloqueado)"
            elif interferencia_estimada == -20:
                estado_canais[sensor_ch]["cor_estado"] = "Roxo (Terceiro bloqueado)"
        
        # Armazena a interferência estimada para exibição
        estado_canais[sensor_ch]["potencia_interf_dBr"] = interferencia_estimada

    # 5. Exibir resultados do cenário
    for ch, dados in estado_canais.items():
        if dados['estado'] == "Ativo":
            print(f"  Canal {ch}: [{dados['estado']}] | Potência de Interf. WLAN: (Não estimada) | Cor: {dados['cor_estado']}")
        else:
            print(f"  Canal {ch}: [{dados['estado']}] | Potência de Interf. WLAN: {dados['potencia_interf_dBr']} dBr | Cor: {dados['cor_estado']}")

    return estado_canais

# --- Definição dos Dados dos Cenários com base na Figura ---

# Definição dos canais de sensores ativos e dos canais WLAN que causam interferência
cenarios = {
    'a': {'canais_sensores': [15, 16, 17, 18, 19, 20], 'canais_wlan': range(17, 19), 'limiar_bloqueio': -34},
    'b': {'canais_sensores': range(14, 22), 'canais_wlan': range(16, 20), 'limiar_bloqueio': -34},
    'c': {'canais_sensores': range(14, 22), 'canais_wlan': range(16, 20), 'limiar_bloqueio': -24},
    'd': {'canais_sensores': range(14, 22), 'canais_wlan': range(15, 21), 'limiar_bloqueio': -20},
    'e': {'canais_sensores': range(14, 23), 'canais_wlan': range(15, 21), 'limiar_bloqueio': -20}, # Cenario 'e' adiciona canal 22
}

# --- Execução da Simulação para todos os Cenários ---

# Itera sobre cada cenário definido e executa a função de estimativa
for id_cenario, dados_cenario in cenarios.items():
    # Os limiares de bloqueio foram inferidos a partir dos resultados mostrados na figura.
    # Por exemplo, no cenário 'b', o canal 17 está bloqueado com -34dBr, enquanto no 'c' está ativo com 0dBr.
    # Isso implica que no 'b', o limiar é -34dBr, e no 'c' é mais rigoroso, como -24dBr.
    estimar_interferencia_wlan(id_cenario, 
                               dados_cenario['canais_sensores'], 
                               dados_cenario['canais_wlan'], 
                               dados_cenario['limiar_bloqueio'])

print("\n--- Simulação Concluída ---")