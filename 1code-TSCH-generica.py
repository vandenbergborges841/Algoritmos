import time

class TSCHNode:
    def __init__(self, node_id, channels):
        self.node_id = node_id
        self.channels = channels
        self.num_channels = len(channels)
        self.asn = 0  # Absolute Slot Number
        
    def get_frequency(self, channel_offset):
        """Calcula o canal atual baseado no ASN e Offset"""
        index = (self.asn + channel_offset) % self.num_channels
        return self.channels[index]

    def run_slot(self, slot_type, channel_offset):
        """Simula a execução de um Time Slot"""
        freq = self.get_frequency(channel_offset)
        
        print(f"[ASN: {self.asn:03d}] Nó {self.node_id} no Canal {freq} MHz | Tipo: {slot_type}")
        
        # Lógica de transmissão/recepção
        if slot_type == "TX":
            print(f"  >> Transmitindo dados...")
        elif slot_type == "RX":
            print(f"  << Aguardando pacotes...")
            
        # Incrementa o ASN ao final de cada slot (Sincronização)
        self.asn += 1

# --- Configurações da Rede ---
IEEE_802_15_4_CHANNELS = [2405, 2410, 2415, 2420, 2425, 2430, 2435, 2440, 
                          2445, 2450, 2455, 2460, 2465, 2470, 2475, 2480]

# Criando o nó (ex: um sensor de umidade)
sensor_node = TSCHNode(node_id="Sensor_01", channels=IEEE_802_15_4_CHANNELS)

# Definição simples de um Slotframe (Ciclo de comunicação)
# 0 = TX, 1 = Dormir, 2 = Dormir
slotframe_config = {0: "TX", 1: "Sleep", 2: "Sleep"}
my_offset = 5  # Offset fixo para este link

print(f"Iniciando Simulação TSCH...\n")

try:
    for i in range(10):  # Simula 10 slots de tempo
        current_slot = i % 3  # Tamanho do slotframe = 3
        
        action = slotframe_config.get(current_slot, "Sleep")
        
        if action != "Sleep":
            sensor_node.run_slot(action, my_offset)
        else:
            print(f"[ASN: {sensor_node.asn:03d}] Nó {sensor_node.node_id} em modo SLEEP (Economia de Energia)")
            sensor_node.asn += 1
            
        time.sleep(0.5)  # Delay apenas para visualização no terminal

except KeyboardInterrupt:
    print("\nSimulação encerrada.")