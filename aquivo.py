import serial.tools.list_ports

portas = serial.tools.list_ports.comports()
if portas:
    print("Portas seriais disponíveis:")
    for p in portas:
        print(f"  - {p.device}")
else:
    print("Nenhuma porta serial encontrada. Verifique a conexão do micro:bit.")