import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import Calendar
import pandas as pd
from datetime import datetime, timedelta
import csv

# Função para mostrar o calendário do mês selecionado
def show_calendar():
    year = int(year_entry.get())
    month = month_combo.current() + 1

    calendar_frame.grid(row=3, column=0, columnspan=2)
    cal.config(year=year, month=month)

# Função para gerar a escala automaticamente
def generate_schedule():
    year = int(year_entry.get())
    month = month_combo.current() + 1
    first_day = datetime(year, month, 1)
    num_days = (first_day.replace(month=month % 12 + 1, day=1) - timedelta(days=1)).day
    
    global schedule
    schedule = {}
    for day in range(num_days):
        current_date = first_day + timedelta(days=day)
        schedule[current_date] = assign_team(current_date)
    
    display_schedule(schedule)

# Função para atribuir uma equipe para uma data específica
def assign_team(date):
    available_motoristas = [m for m in motoristas if is_available(m, date)]
    available_socorristas = [s for s in socorristas if is_available(s, date)]
    
    if len(available_motoristas) < 1 or len(available_socorristas) < 1:
        return "Equipe incompleta"
    
    motorista = available_motoristas[0]
    socorrista = available_socorristas[0]
    
    return f"Motorista: {motorista['nome']}, Socorrista: {socorrista['nome']}"

# Função para verificar se um membro da equipe está disponível
def is_available(member, date):
    return member['disponibilidades'].get(date.strftime('%Y-%m-%d'), False)

# Função para mostrar a escala gerada
def display_schedule(schedule):
    schedule_text.set("\n".join([f"{date.strftime('%d-%m-%Y')}: {team}" for date, team in schedule.items()]))

# Função para salvar a escala em um arquivo CSV
def save_schedule():
    if not schedule:
        messagebox.showwarning("Aviso", "Não há escala para salvar!")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Data", "Escala"])
        for date, team in schedule.items():
            writer.writerow([date.strftime('%d-%m-%Y'), team])
    messagebox.showinfo("Sucesso", "Escala salva com sucesso!")

# Função para carregar a escala de um arquivo CSV
def load_schedule():
    global schedule
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    schedule = {}
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Pular o cabeçalho
        for row in reader:
            date = datetime.strptime(row[0], '%d-%m-%Y')
            schedule[date] = row[1]
    display_schedule(schedule)
    messagebox.showinfo("Sucesso", "Escala carregada com sucesso!")

# Função para imprimir a escala
def print_schedule():
    if not schedule:
        messagebox.showwarning("Aviso", "Não há escala para imprimir!")
        return

    # Imprimir usando o sistema operacional (simulação de impressão)
    print_text = "\n".join([f"{date.strftime('%d-%m-%Y')}: {team}" for date, team in schedule.items()])
    print(print_text)
    messagebox.showinfo("Imprimir", "A escala foi enviada para impressão.")

# Função para adicionar um membro à equipe
def add_member():
    member_type = member_type_var.get()
    name = name_entry.get()
    if member_type == "Motorista":
        motoristas.append({'nome': name, 'disponibilidades': {}, 'indisponibilidades': []})
    elif member_type == "Socorrista":
        socorristas.append({'nome': name, 'disponibilidades': {}, 'indisponibilidades': []})
    update_member_list()

# Função para remover um membro da equipe
def remove_member():
    selected_member = member_listbox.get(tk.ACTIVE)
    if not selected_member:
        return
    member_name = selected_member.split(": ")[1]
    member_type = selected_member.split(": ")[0]
    if member_type == "Motorista":
        motoristas[:] = [m for m in motoristas if m['nome'] != member_name]
    elif member_type == "Socorrista":
        socorristas[:] = [s for s in socorristas if s['nome'] != member_name]
    update_member_list()

# Função para atualizar a lista de membros na interface
def update_member_list():
    member_listbox.delete(0, tk.END)
    for motorista in motoristas:
        member_listbox.insert(tk.END, f"Motorista: {motorista['nome']}")
    for socorrista in socorristas:
        member_listbox.insert(tk.END, f"Socorrista: {socorrista['nome']}")

# Função para definir as disponibilidades de um membro
def set_availability():
    selected_member = member_listbox.get(tk.ACTIVE)
    if not selected_member:
        return
    member_name = selected_member.split(": ")[1]
    member_type = selected_member.split(": ")[0]
    member = None
    if member_type == "Motorista":
        member = next((m for m in motoristas if m['nome'] == member_name), None)
    elif member_type == "Socorrista":
        member = next((s for s in socorristas if s['nome'] == member_name), None)
    if member is None:
        return
    
    def save_availability():
        year = int(year_entry.get())
        month = month_combo.current() + 1
        first_day = datetime(year, month, 1)
        num_days = (first_day.replace(month=month % 12 + 1, day=1) - timedelta(days=1)).day
        for day in range(num_days):
            current_date = first_day + timedelta(days=day)
            member['disponibilidades'][current_date.strftime('%Y-%m-%d')] = availability_var.get() == 1
        availability_window.destroy()

    availability_window = tk.Toplevel(root)
    availability_window.title(f"Definir Disponibilidade para {member_name}")
    availability_var = tk.IntVar()
    available_radio = tk.Radiobutton(availability_window, text="Disponível", variable=availability_var, value=1)
    unavailable_radio = tk.Radiobutton(availability_window, text="Indisponível", variable=availability_var, value=0)
    save_button = tk.Button(availability_window, text="Salvar", command=save_availability)
    available_radio.pack()
    unavailable_radio.pack()
    save_button.pack()

# Cria a interface gráfica
root = tk.Tk()
root.title("Calendário Dinâmico para Escala de Serviço")

# Widgets de seleção de mês e ano
month_label = tk.Label(root, text="Selecione o mês:")
month_label.grid(row=0, column=0)
month_combo = ttk.Combobox(root, values=["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
month_combo.grid(row=0, column=1)

year_label = tk.Label(root, text="Selecione o ano:")
year_label.grid(row=1, column=0)
year_entry = tk.Entry(root)
year_entry.grid(row=1, column=1)

show_button = tk.Button(root, text="Mostrar Calendário", command=show_calendar)
show_button.grid(row=2, column=0, columnspan=2)

# Calendário
calendar_frame = tk.Frame(root)
cal = Calendar(calendar_frame, selectmode="day")
cal.grid(row=0, column=0, columnspan=2)

# Botão para gerar a escala automaticamente
generate_button = tk.Button(root, text="Gerar Escala", command=generate_schedule)
generate_button.grid(row=3, column=0, columnspan=2)

# Botões para salvar, carregar e imprimir escala
save_button = tk.Button(root, text="Salvar Escala", command=save_schedule)
save_button.grid(row=4, column=0)
load_button = tk.Button(root, text="Carregar Escala", command=load_schedule)
load_button.grid(row=4, column=1)
print_button = tk.Button(root, text="Imprimir Escala", command=print_schedule)
print_button.grid(row=5, column=0, columnspan=2)

# Label para mostrar a escala gerada
schedule_text = tk.StringVar()
schedule_label = tk.Label(root, textvariable=schedule_text)
schedule_label.grid(row=6, column=0, columnspan=2)

# Interface para gerenciar membros da equipe
member_type_var = tk.StringVar()
member_type_var.set("Motorista")
motorista_radio = tk.Radiobutton(root, text="Motorista", variable=member_type_var, value="Motorista")
socorrista_radio = tk.Radiobutton(root, text="Socorrista", variable=member_type_var, value="Socorrista")
motorista_radio.grid(row=7, column=0)
socorrista_radio.grid(row=7, column=1)

name_label = tk.Label(root, text="Nome:")
name_label.grid(row=8, column=0)
name_entry = tk.Entry(root)
name_entry.grid(row=8, column=1)

add_member_button = tk.Button(root, text="Adicionar Membro", command=add_member)
add_member_button.grid(row=9, column=0, columnspan=2)
remove_member_button = tk.Button(root, text="Remover Membro", command=remove_member)
remove_member_button.grid(row=10, column=0, columnspan=2)

member_listbox = tk.Listbox(root)
member_listbox.grid(row=11, column=0, columnspan=2)
update_member_list()

set_availability_button = tk.Button(root, text="Definir Disponibilidade", command=set_availability)
set_availability_button.grid(row=12, column=0, columnspan=2)

# Dados de exemplo para motoristas e socorristas
motoristas = [
    {'nome': 'Motorista 1', 'disponibilidades': {}, 'indisponibilidades': []},
    {'nome': 'Motorista 2', 'disponibilidades': {}, 'indisponibilidades': [datetime(2024, 6, 15)]}
]

socorristas = [
    {'nome': 'Socorrista 1', 'disponibilidades': {}, 'indisponibilidades': []},
    {'nome': 'Socorrista 2', 'disponibilidades': {}, 'indisponibilidades': [datetime(2024, 6, 10)]}
]

# Variável global para armazenar a escala gerada
schedule = {}

root.mainloop()
