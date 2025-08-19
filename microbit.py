import serial
from time import sleep
import tkinter as tk
from tkinter import ttk

# Mude a porta serial para a que corresponde ao seu micro:bit
PORTA_SERIAL = 'COM4'
VELOCIDADE = 115200

velocidade = 1
valor_atual = 0

# Configura a janela do medidor
janela = tk.Tk()
janela.title("Medidor do Micro:bit")
janela.geometry("400x150")

# Cria a barra de progresso
label_porcentagem = tk.Label(janela, text="0%", font=("Helvetica", 24))
label_porcentagem.pack(pady=10)

progresso_barra = ttk.Progressbar(janela, orient='horizontal', length=300, mode='determinate')
progresso_barra.pack(pady=10)

# Função para ler dados do micro:bit e atualizar o medidor

def atualizar_medidor():
    global valor_atual, velocidade
    try:
        # Tenta ler uma linha do micro:bit
        linha = ser.readline().decode('utf-8').strip()
        print('linha ', linha == '1', ' atual', valor_atual)
        if linha == '1':
            if velocidade == 0:
                velocidade = 1
            sleep(0.002)
            valor_atual += 10 * velocidade
            
            # Atualiza o valor da barra de progresso e o texto
            progresso_barra['value'] = valor_atual
            label_porcentagem.config(text=f"{valor_atual}%")

            # Reseta a barra e o texto quando chega a 100
            if valor_atual >= 100 or valor_atual <= 0:
                velocidade *= -1
        else:
            velocidade = 0


    except Exception as e:
        print(f"Erro de leitura: {e}")
        
    janela.after(100, atualizar_medidor)

# Tenta conectar à porta serial
try:
    ser = serial.Serial(PORTA_SERIAL, VELOCIDADE, timeout=1)
    print(f"Conectado à porta {PORTA_SERIAL}")
    janela.after(100, atualizar_medidor)
    janela.mainloop()
except serial.SerialException as e:
    print(f"Não foi possível conectar à porta {PORTA_SERIAL}: {e}")
    print("Verifique se o micro:bit está conectado e a porta está correta.")