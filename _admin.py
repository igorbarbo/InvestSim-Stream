# criar_admin.py
from Modules.database import criar_usuario

# Altere os dados conforme desejar
criar_usuario("admin", "Administrador", "1234")
print("Usuário admin criado com senha 1234")
