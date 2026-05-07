import random

class BlacklistManager:
    def __init__(self, all_channels):
        self.all_channels = all_channels
        self.active_sequence = list(all_channels)
        self.blacklist = []
        self.stats = {ch: {"success": 0, "total": 0} for ch in all_channels}
        self.threshold = 0.6  # 60% de sucesso mínimo exigido

    def get_pdr(self, channel):
        """Calcula o Packet Delivery Ratio (Taxa de Entrega)"""
        s = self.stats[channel]
        return s["success"] / s["total"] if s["total"] > 0 else 1.0

    def record_attempt(self, channel, success):
        """Registra o resultado de uma transmissão"""
        self.stats[channel]["total"] += 1
        if success:
            self.stats[channel]["success"] += 1
        
        # Avalia se deve ir para a blacklist
        pdr = self.get_pdr(channel)
        if pdr < self.threshold and channel not in self.blacklist:
            print(f"⚠️ ALERTA: Canal {channel} detectado como instável (PDR: {pdr:.2%}). Blacklisting...")
            self.update_blacklist(channel, add=True)
        elif pdr >= self.threshold and channel in self.blacklist:
            print(f"✅ RECUPERADO: Canal {channel} voltou a ficar estável. Reintegrando...")
            self.update_blacklist(channel, add=False)

    def update_blacklist(self, channel, add=True):
        """Atualiza a lista de canais ativos"""
        if add and channel in self.active_sequence:
            self.active_sequence.remove(channel)
            self.blacklist.append(channel)
        elif not add and channel in self.blacklist:
            self.blacklist.remove(channel)
            self.active_sequence.append(channel)
            self.active_sequence.sort()

    def get_next_hop(self, asn):
        """Calcula o canal ignorando os que estão na Blacklist"""
        if not self.active_sequence:
            return None  # Todos os canais estão ruins!
        
        # A sequência de saltos agora só usa canais 'limpos'
        idx = asn % len(self.active_sequence)
        return self.active_sequence[idx]

# --- Simulação de Ambiente ---
# Canais 11 a 26 (Padrão 802.15.4)
manager = BlacklistManager(list(range(11, 27)))

print(f"Canais Ativos Iniciais: {manager.active_sequence}\n")

# Simulação de 50 transmissões
for asn in range(50):
    ch = manager.get_next_hop(asn)
    
    # Simulando interferência pesada nos canais 15 e 16 (ex: Wi-Fi próximo)
    if ch in [15, 16]:
        success = random.random() > 0.8  # 80% de chance de falha
    else:
        success = random.random() > 0.1  # 10% de chance de falha
    
    manager.record_attempt(ch, success)

print(f"\n--- Estado Final da Rede ---")
print(f"Canais Ativos: {manager.active_sequence}")
print(f"Blacklist: {manager.blacklist}")