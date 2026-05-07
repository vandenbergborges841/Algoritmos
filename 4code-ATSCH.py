import random
import time

class ATSCH_Node:
    def __init__(self, node_id, channels):
        self.node_id = node_id
        self.asn = 0
        self.channels = channels
        # Qualidade inicial do canal (0.0 a 1.0)
        self.channel_quality = {ch: 1.0 for ch in channels}
        self.blacklist_threshold = 0.4
        
    def get_adaptive_channel(self, channel_offset):
        """
        Lógica Adaptativa: Tenta o canal padrão do TSCH. 
        Se estiver ruim, busca o melhor canal disponível.
        """
        # Cálculo padrão TSCH
        standard_idx = (self.asn + channel_offset) % len(self.channels)
        target_ch = self.channels[standard_idx]
        
        # Verificação adaptativa
        if self.channel_quality[target_ch] < self.blacklist_threshold:
            # Seleciona o canal com a melhor qualidade atual
            target_ch = max(self.channel_quality, key=self.channel_quality.get)
            mode = "ADAPTATIVO (Substituição)"
        else:
            mode = "PADRÃO"
            
        return target_ch, mode

    def simulate_transmission(self, channel):
        """
        Simula o ambiente físico. 
        Canais altos (ex: > 2470) terão interferência simulada.
        """
        interference = 0.8 if channel > 2470 else 0.1
        success = random.random() > interference
        return success

    def update_quality(self, channel, success):
        """Atualiza a qualidade do canal usando média móvel exponencial"""
        alpha = 0.2  # Fator de aprendizado
        result = 1.0 if success else 0.0
        self.channel_quality[channel] = (1 - alpha) * self.channel_quality[channel] + alpha * result

    def run_slot(self, channel_offset):
        channel, mode = self.get_adaptive_channel(channel_offset)
        success = self.simulate_transmission(channel)
        
        self.update_quality(channel, success)
        
        status = "✅ SUCESSO" if success else "❌ FALHA/COLISÃO"
        print(f"[ASN: {self.asn:03d}] Canal: {channel}MHz | Modo: {mode} | Status: {status}")
        
        self.asn += 1

# --- Execução ---
CHANNELS_802154 = [2405, 2410, 2415, 2470, 2475, 2480] # Alguns canais bons, outros ruins
node = ATSCH_Node("Node_Adaptive_01", CHANNELS_802154)

print(f"Iniciando ATSCH - Monitorando {len(CHANNELS_802154)} canais...\n")

for _ in range(20):
    node.run_slot(channel_offset=2)
    time.sleep(0.2)

print("\n--- Relatório Final de Qualidade dos Canais ---")
for ch, qual in node.channel_quality.items():
    print(f"Canal {ch}MHz: {qual:.2%}")