import hashlib
import time

class WirelessHARTNode:
    def __init__(self, node_id, manager_key):
        self.node_id = node_id
        self.asn = 0  # Absolute Slot Number
        self.manager_key = manager_key
        self.channels = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
        
    def calculate_channel(self, channel_offset):
        """
        No WirelessHART, o salto de canal é calculado para evitar interferências.
        F = (ASN + channel_offset) % 16
        """
        channel_index = (self.asn + channel_offset) % len(self.channels)
        return self.channels[channel_index]

    def execute_slot(self, slot_config):
        """Executa a tarefa designada para o slot atual"""
        slot_type = slot_config['type']
        offset = slot_config['offset']
        channel = self.calculate_channel(offset)
        
        print(f"[ASN: {self.asn:04d}] Slot {self.asn % 10} | Canal: {channel} | ", end="")
        
        if slot_type == "TX":
            payload = f"TEMP_DATA_{self.node_id}_25.5C"
            mic = self.generate_mic(payload)
            print(f"TX Node {self.node_id}: {payload} | MIC: {mic}")
        elif slot_type == "RX":
            print(f"RX Mode: Aguardando ACK ou Comando...")
        else:
            print("SLEEP: Economizando bateria.")

        self.asn += 1

    def generate_mic(self, data):
        """Simula o Message Integrity Code para segurança industrial"""
        token = f"{data}{self.asn}{self.manager_key}"
        return hashlib.sha256(token.encode()).hexdigest()[:4].upper()

# --- Configuração do Network Manager ---
# Definimos um Superframe de 10 slots (1 slot = 10ms no padrão real)
# Slot 0: Transmissão de dados
# Slot 1: Recepção de ACK
# Outros: Sleep
superframe = {
    0: {"type": "TX", "offset": 2},
    1: {"type": "RX", "offset": 5}
}

sensor_field = WirelessHARTNode(node_id="WH_001", manager_key="SECURE_KEY_123")

print("--- Operação WirelessHART Iniciada ---")
try:
    for _ in range(15):  # Simula 15 slots
        slot_index = sensor_field.asn % 10  # Tamanho do Superframe = 10
        
        config = superframe.get(slot_index, {"type": "SLEEP", "offset": 0})
        sensor_field.execute_slot(config)
        
        # Na realidade, cada slot dura exatamente 10ms
        time.sleep(0.1) 

except KeyboardInterrupt:
    print("\nRede desligada.")