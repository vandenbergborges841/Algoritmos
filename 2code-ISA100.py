import datetime
import hashlib

class ISA100Node:
    def __init__(self, device_id, channel_list):
        self.device_id = device_id
        self.channels = channel_list
        self.asn = 0  # Absolute Slot Number
        self.tai_time = datetime.datetime.now() # Tempo Atômico Internacional (referência)

    def calculate_hopping_channel(self, slot_offset, channel_offset):
        """
        Calcula o canal físico baseado na função de hopping do ISA100.11a.
        f = (ASN + channel_offset) mod num_channels
        """
        num_ch = len(self.channels)
        channel_index = (self.asn + channel_offset) % num_ch
        return self.channels[channel_index]

    def send_packet(self, data, slot_offset, ch_offset):
        """Simula o envio de um pacote em um slot específico"""
        freq = self.calculate_hopping_channel(slot_offset, ch_offset)
        
        # Simulação de segurança (MIC - Message Integrity Code) simplificada
        mic = hashlib.md5(f"{data}{self.asn}".encode()).hexdigest()[:8]
        
        print(f"[ASN: {self.asn:04d}] 📶 Frequência: {freq}MHz")
        print(f"      Node {self.device_id} -> Enviando: '{data}' | MIC: {mic}")
        
    def increment_asn(self):
        self.asn += 1

# --- Configuração da Rede Industrial ---
# Canais padrão 802.15.4 (2.4 GHz)
CHANNELS = [2405 + 5*i for i in range(16)]

# O System Manager define o escalonamento (Schedule)
# Slot 0: Publicação de dados (TX)
# Slot 1: Recebimento de comando (RX)
# Slot 2-4: Sleep (Economia de energia)
schedule = {
    0: {"type": "TX", "ch_offset": 3, "label": "Data_Publish"},
    1: {"type": "RX", "ch_offset": 7, "label": "DL_Command"}
}

node = ISA100Node("SENS-PRESS-01", CHANNELS)

print("--- Iniciando Operação ISA100.11a ---")

for _ in range(10):  # Simulando 10 slots de tempo
    current_slot_in_frame = node.asn % 5  # Slotframe de tamanho 5
    
    if current_slot_in_frame in schedule:
        slot_info = schedule[current_slot_in_frame]
        
        if slot_info["type"] == "TX":
            node.send_packet("P=102.4bar", current_slot_in_frame, slot_info["ch_offset"])
        else:
            print(f"[ASN: {node.asn:04d}] 📥 Escutando comandos no Offset {slot_info['ch_offset']}...")
    else:
        print(f"[ASN: {node.asn:04d}] 💤 Modo Low Power (Deep Sleep)")
    
    node.increment_asn()