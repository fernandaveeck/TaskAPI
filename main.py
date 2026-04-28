from fastapi import FastAPI, HTTPException
import json
from pydantic import BaseModel, Field

#inicia a aplicação FastApi
app = FastAPI()

class Task(BaseModel):
    title: str = Field(..., example="Fazer compras")
    description: str = Field(..., example="Comprar leite, pão e ovos")
    owner: str = Field(..., example="João")
    status: str = Field(..., example="Pendente")
    comments: list[str] = Field(default_factory=list, example=["Comentário 1", "Comentário 2"])

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

@app.post("/tasks")
async def create_task(task: Task):
    tasks = await ler_arquivo_json()
    #Pega o ultimo id da lista e itera sobre caso não tenha inicial 
    # com 0 e depois incrementa 1
    last_id = tasks["tasks"][-1]["id"] if tasks["tasks"] else 0
    new_task = task.model_dump()
    new_task["id"] = last_id + 1
    tasks["tasks"].append(new_task)
    with open("tasks.json", "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)
    return new_task

@app.put("/tasks/{id}")
async def update_task(id: int, task: Task):
    tasks_data = await ler_arquivo_json()
    tasks_list = tasks_data["tasks"]
    index = next((i for i, item in enumerate(tasks_list) if item["id"] == id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Task not found")
    updated = task.model_dump()
    updated["id"] = id
    tasks_list[index] = updated
    with open("tasks.json", "w", encoding="utf-8") as f:
        json.dump(tasks_data, f, ensure_ascii=False, indent=4)
    return updated

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