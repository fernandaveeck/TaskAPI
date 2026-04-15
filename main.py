from fastapi import FastAPI, HTTPException
import json

#inicia a aplicação FastApi
app = FastAPI()

#define um get simples da rota padrão URL ("/")
@app.get("/") #paramêtro que indica qual verbo será executado
async def get_root_message(): #define o nome da função
    return {"message": "Hello World"} #retorna um json com a mensagem "Hello World"

#buscar todas as tasks
@app.get("/tasks")
async def buscar_todos():
    dados = await ler_arquivo_json()
    return dados["tasks"]

#buscar tasks por id
@app.get("/tasks/{id}") #{id} = path param (é uma variável)
async def busca_por_id(id: int):
    dados = await ler_arquivo_json()
    lista_de_dados = dados["tasks"]
    tarefa = next((item for item in lista_de_dados if item["id"] == id), None) #função de compressão de lista
    if tarefa is None:
        raise HTTPException(status_code = 404, detail="Not found")
    return tarefa

#deletar task
@app.delete("/tasks/{id}")
async def deletar_tarefa(id: int):
    dados = await ler_arquivo_json()
    dados["tasks"] = [item for item in dados["tasks"] if item["id"] != id]
    with open("tasks.json", "w", encoding = "UTF-8") as f:
        json.dump(dados, f, ensure_ascii= False, indent=4)
        return {"message": "Tarefa deletada com sucesso!"}

#função para ler um json
async def ler_arquivo_json():
     with open("tasks.json", encoding = "utf-8") as f:
         dados = json.load(f)
         return dados