# Loja Personalizável - Backend (Django + Supabase)

API RESTful em **Django** que serve como cérebro do sandbox de lojas online.  
Cada usuário autenticado possui sua própria loja isolada 
Autenticação via **JWT** (Simple JWT) e banco de dados + storage + realtime via **Supabase**.

O frontend consome esta API e usa o mesmo JWT para identificar e isolar as lojas de cada usuário.

<br/>

##  Principais Características

- Cadastro, login e refresh de tokens JWT
- Isolamento total de dados: cada usuário só vê/edita sua própria loja
- CRUD de Loja = produtos, categorias
- Upload de arquivos fotos de produtos → **Supabase Storage**
