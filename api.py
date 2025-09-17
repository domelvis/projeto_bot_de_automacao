# api.py - API REST com suporte ao Dashboard
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from models import Database
from typing import List, Optional
import uvicorn
import os

# Inicializar FastAPI
app = FastAPI(
    title="Bot Automation API",
    description="API para gerenciar bots de automação",
    version="1.0.0"
)

# Servir arquivos estáticos do frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Inicializar banco de dados
db = Database()

# Modelos Pydantic para validação
class BotCreate(BaseModel):
    name: str
    description: Optional[str] = ""

class BotResponse(BaseModel):
    id: int
    name: str
    description: str
    status: str
    created_at: str

class ExecutionResponse(BaseModel):
    id: int
    bot_id: int
    status: str
    start_time: str
    end_time: Optional[str] = None
    error_message: Optional[str] = None

# Rotas da API
@app.get("/")
async def root():
    """Redirecionar para o dashboard"""
    return FileResponse('frontend/dashboard.html')

@app.get("/dashboard")
async def dashboard():
    """Servir dashboard"""
    return FileResponse('frontend/dashboard.html')

@app.get("/api")
async def api_info():
    """Informações da API"""
    return {"message": "Bot Automation API funcionando!", "version": "1.0.0"}

@app.post("/bots/", response_model=dict)
async def create_bot(bot: BotCreate):
    """Criar um novo bot"""
    try:
        bot_id = db.create_bot(bot.name, bot.description)
        return {"message": "Bot criado com sucesso!", "bot_id": bot_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bots/")
async def list_bots():
    """Listar todos os bots"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bots ORDER BY created_at DESC")
        bots = cursor.fetchall()
        conn.close()
        
        # Converter para formato JSON
        bots_list = []
        for bot in bots:
            bots_list.append({
                "id": bot[0],
                "name": bot[1],
                "description": bot[2],
                "status": bot[3],
                "created_at": bot[4],
                "last_run": bot[5]
            })
        
        return {"bots": bots_list, "total": len(bots_list)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bots/{bot_id}")
async def get_bot(bot_id: int):
    """Obter detalhes de um bot específico"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bots WHERE id = ?", (bot_id,))
        bot = cursor.fetchone()
        conn.close()
        
        if not bot:
            raise HTTPException(status_code=404, detail="Bot não encontrado")
        
        return {
            "id": bot[0],
            "name": bot[1],
            "description": bot[2],
            "status": bot[3],
            "created_at": bot[4],
            "last_run": bot[5]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bots/{bot_id}/start")
async def start_bot(bot_id: int):
    """Iniciar execução de um bot"""
    try:
        # Verificar se bot existe
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bots WHERE id = ?", (bot_id,))
        bot = cursor.fetchone()
        
        if not bot:
            raise HTTPException(status_code=404, detail="Bot não encontrado")
        
        # Criar nova execução
        execution_id = db.start_execution(bot_id)
        
        # Atualizar status do bot
        cursor.execute(
            "UPDATE bots SET status = 'running', last_run = CURRENT_TIMESTAMP WHERE id = ?", 
            (bot_id,)
        )
        conn.commit()
        conn.close()
        
        return {
            "message": "Bot iniciado com sucesso!", 
            "execution_id": execution_id,
            "bot_id": bot_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bots/{bot_id}/stop")
async def stop_bot(bot_id: int):
    """Parar execução de um bot"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Atualizar status do bot
        cursor.execute("UPDATE bots SET status = 'stopped' WHERE id = ?", (bot_id,))
        
        # Finalizar execuções pendentes
        cursor.execute('''
            UPDATE executions 
            SET status = 'stopped', end_time = CURRENT_TIMESTAMP 
            WHERE bot_id = ? AND status = 'running'
        ''', (bot_id,))
        
        conn.commit()
        conn.close()
        
        return {"message": "Bot parado com sucesso!", "bot_id": bot_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bots/{bot_id}/executions")
async def get_bot_executions(bot_id: int):
    """Obter histórico de execuções de um bot"""
    try:
        executions = db.get_bot_history(bot_id)
        
        executions_list = []
        for exec in executions:
            executions_list.append({
                "id": exec[0],
                "bot_id": exec[1],
                "status": exec[2],
                "start_time": exec[3],
                "end_time": exec[4],
                "error_message": exec[5],
                "screenshots_count": exec[6]
            })
        
        return {"executions": executions_list, "total": len(executions_list)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Estatísticas gerais do sistema"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Total de bots
        cursor.execute("SELECT COUNT(*) FROM bots")
        total_bots = cursor.fetchone()[0]
        
        # Total de execuções
        cursor.execute("SELECT COUNT(*) FROM executions")
        total_executions = cursor.fetchone()[0]
        
        # Execuções bem sucedidas
        cursor.execute("SELECT COUNT(*) FROM executions WHERE status = 'completed'")
        successful_executions = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_bots": total_bots,
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": f"{(successful_executions/total_executions*100):.1f}%" if total_executions > 0 else "0%"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Executar a API
if __name__ == "__main__":
    print("🚀 Iniciando Bot Automation API...")
    print("📖 Documentação: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)