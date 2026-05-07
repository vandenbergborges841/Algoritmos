import random

class IEEE802154_TSCH_Manager:
    def __init__(self, channels, analysis_period=30):
        self.asn = 0  # Absolute Slot Number
        self.all_channels = channels
        self.analysis_period = analysis_period
        
        # Rankings e Listas
        self.blacklist = set()
        self.ranked_channels = list(channels) # Ordenados por qualidade
        
        # Estatísticas de longo prazo para cada canal
        self.stats = {ch: {"success": 0, "total": 0, "pdr": 1.0} for ch in channels}
        
        # Configurações de limite
        self.pdr_threshold = 0.70  # Bloqueia abaixo de 70%

    def get_hopping_channel(self, channel_offset):
        """Calcula o canal seguindo o padrão IEEE 802.15.4e + Re-mapeamento por Ranking"""
        # Cálculo base do TSCH
        idx = (self.asn + channel_offset) % len(self.all_channels)
        target_ch = self.all_channels[idx]

        # Se o canal estiver na Blacklist, usamos o "Melhor da Classe" (Ranking index 0)
        if target_ch in self.blacklist:
            # Seleciona o melhor canal disponível que não está na blacklist
            best_available = [ch for ch in self.ranked_channels if ch not in self.blacklist]
            
            if not best_available:
                return target_ch, "EMERGÊNCIA (Todos os canais em falha)"
            
            # Usa o melhor canal do ranking de forma determinística
            selected_ch = best_available[self.asn % len(best_available)]
            return selected_ch, f"RE-MAPEADO (Best: {selected_ch})"
        
        return target_ch, "PADRÃO"

    def record_transmission(self, channel, success):
        """Registra o evento de transmissão"""
        self.stats[channel]["total"] += 1
        if success:
            self.stats[channel]["success"] += 1
        
        # Atualiza o PDR instantâneo do canal
        s = self.stats[channel]
        self.stats[channel]["pdr"] = s["success"] / s["total"]

    def perform_scheduled_reanalysis(self):
        """Reanálise Programada: Bloqueia, Desbloqueia e Ordena"""
        print(f"\n--- 📊 REANÁLISE PROGRAMADA (ASN: {self.asn}) ---")
        
        # 1. Atualizar Blacklist
        for ch, data in self.stats.items():
            if data["total"] > 0:
                if data["pdr"] < self.pdr_threshold:
                    if ch not in self.blacklist:
                        print(f"❌ Canal {ch} inserido na Blacklist (PDR: {data['pdr']:.1%})")
                        self.blacklist.add(ch)
                else:
                    if ch in self.blacklist:
                        print(f"✅ Canal {ch} recuperado e liberado (PDR: {data['pdr']:.1%})")
                        self.blacklist.remove(ch)

        # 2. Ordenar Canais por Qualidade (Ordem Decrescente de PDR)
        # Canais com mais sucesso ficam no topo para serem usados como substitutos
        self.ranked_channels.sort(key=lambda x: self.stats[x]["pdr"], reverse=True)
        
        print(f"Ranking de Canais (Melhor -> Pior): {self.ranked_channels}")
        print(f"Blacklist Atual: {list(self.blacklist)}")
        print("--------------------------------------------------\n")

    def run_slot(self, offset):
        """Simula a execução de um Time Slot TSCH"""
        channel, mode = self.get_hopping_channel(offset)
        
        # Simulação de Interferência Variável (Canais 15, 16 e 20 estão ruins)
        noise_map = {15: 0.8, 16: 0.9, 20: 0.7}
        fail_chance = noise_map.get(channel, 0.1) # 10% de falha padrão, ou valor do mapa
        
        success = random.random() > fail_chance
        self.record_transmission(channel, success)
        
        status = "✔" if success else "✘"
        print(f"ASN {self.asn:03d} | Canal: {channel:2} | Modo: {mode:25} | Status: {status}")
        
        self.asn += 1
        if self.asn % self.analysis_period == 0:
            self.perform_scheduled_reanalysis()

# --- Instanciação e Teste ---
canais_802154 = list(range(11, 27)) # 16 canais (2.4 GHz)
rede = IEEE802154_TSCH_Manager(canais_802154, analysis_period=25)

print("Iniciando Simulação IEEE 802.15.4 + TSCH + Ranked Blacklist\n")
for _ in range(75):
    rede.run_slot(channel_offset=3)