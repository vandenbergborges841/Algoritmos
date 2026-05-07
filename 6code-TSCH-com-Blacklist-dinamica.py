import random

class TSCH_Advanced_Node:
    def __init__(self, channels, analysis_window=20):
        self.asn = 0  # Absolute Slot Number (Relógio Global)
        self.all_channels = channels
        self.blacklist = set()
        
        # Parâmetros de análise
        self.analysis_window = analysis_window
        self.stats = {ch: {"success": 0, "total": 0} for ch in channels}
        
        # Limiares de Qualidade (PDR - Packet Delivery Ratio)
        self.pdr_block = 0.65    # Bloqueia se sucesso < 65%
        self.pdr_recover = 0.85   # Desbloqueia apenas se > 85%

    def get_hopping_channel(self, channel_offset):
        """Calcula o canal TSCH com desvio de Blacklist"""
        # 1. Cálculo padrão IEEE 802.15.4e
        base_idx = (self.asn + channel_offset) % len(self.all_channels)
        ch_candidate = self.all_channels[base_idx]

        # 2. Se o canal estiver na blacklist, re-mapeia para a lista limpa
        if ch_candidate in self.blacklist:
            whitelist = [c for c in self.all_channels if c not in self.blacklist]
            if not whitelist:
                return ch_candidate, "CRÍTICO (Nenhum canal limpo)"
            
            # Re-mapeamento determinístico para manter sincronia
            new_idx = (self.asn + channel_offset) % len(whitelist)
            return whitelist[new_idx], "RE-MAPEADO"
        
        return ch_candidate, "PADRÃO"

    def record_slot_result(self, channel, success):
        """Registra o desempenho do canal no slot atual"""
        self.stats[channel]["total"] += 1
        if success:
            self.stats[channel]["success"] += 1

    def perform_periodic_reanalysis(self):
        """
        Reanálise programada: decide quem entra e sai da blacklist.
        Deve ser chamada a cada ciclo 'analysis_window'.
        """
        print(f"\n--- 🔄 REANÁLISE PERIÓDICA (ASN: {self.asn}) ---")
        
        for ch in self.all_channels:
            total = self.stats[ch]["total"]
            if total < 3: continue # Ignora se houve pouca amostragem

            pdr = self.stats[ch]["success"] / total

            if ch not in self.blacklist and pdr < self.pdr_block:
                print(f"❌ Canal {ch} BLOQUEADO (PDR: {pdr:.1%})")
                self.blacklist.add(ch)
            elif ch in self.blacklist and pdr >= self.pdr_recover:
                print(f"✅ Canal {ch} RECUPERADO (PDR: {pdr:.1%})")
                self.blacklist.remove(ch)

        # Reseta as estatísticas para a próxima janela de tempo
        self.stats = {ch: {"success": 0, "total": 0} for ch in self.all_channels}
        print(f"Blacklist Atual: {list(self.blacklist) if self.blacklist else 'Vazia'}")
        print("-------------------------------------------\n")

    def step(self, offset):
        """Simula a execução de um Time Slot"""
        channel, mode = self.get_hopping_channel(offset)
        
        # Simulação de ruído: Canal 13 e 14 estão com interferência
        noise_level = 0.8 if channel in [13, 14] else 0.1
        success = random.random() > noise_level
        
        self.record_slot_result(channel, success)
        
        status = "✔" if success else "✘"
        print(f"ASN {self.asn:03d} | Canal: {channel} | Modo: {mode:12} | Status: {status}")
        
        self.asn += 1
        
        # Verifica se atingiu o período programado de reanálise
        if self.asn % self.analysis_window == 0:
            self.perform_periodic_reanalysis()

# --- Execução da Simulação ---
# 16 canais da banda 2.4GHz
rf_band = list(range(11, 27))
sensor_node = TSCH_Advanced_Node(rf_band, analysis_window=30)

print("Iniciando Sistema TSCH Adaptativo com Blacklist...\n")
for _ in range(90): # Simula 90 slots (3 ciclos de reanálise)
    sensor_node.step(channel_offset=7)