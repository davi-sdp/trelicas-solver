from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Tuple
import uvicorn

from solver_core import solve_truss_reactions
from visualizer import generate_truss_diagram

app = FastAPI()

# Monta a pasta de arquivos estáticos (CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configura o Jinja2 para servir templates HTML
templates = Jinja2Templates(directory=".")

class Node(BaseModel):
    x: float
    y: float

class Force(BaseModel):
    magnitude: float
    angle: float
    node: int # Index do nó

class TrussData(BaseModel):
    nodes: List[Node]
    bars: List[Tuple[int, int]] # Tupla de índices de nós
    forces: List[Force]
    supports: Dict[int, int] # {node_index: type (1=fixed, 2=roller)}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve a página HTML principal."""
    return templates.TemplateResponse(
        request=request, 
        name="index.html"
    )

@app.post("/solve")
async def solve_truss(data: TrussData):
    """
    Recebe os dados da treliça, calcula as reações e gera o diagrama.
    """
    try:
        # Extrai os dados para o solver
        nodes_list_of_dicts = [{'x': n.x, 'y': n.y} for n in data.nodes]
        forces_list_of_dicts = [{'magnitude': f.magnitude, 'angle': f.angle, 'node': f.node} for f in data.forces]

        # Chama o core do solver
        solver_results = solve_truss_reactions(
            nodes_list_of_dicts,
            data.bars,
            forces_list_of_dicts,
            data.supports
        )

        # Gera o diagrama
        diagram_base64 = generate_truss_diagram(
            solver_results['coords_x'],
            solver_results['coords_y'],
            data.bars, # Usar as barras originais para o desenho
            solver_results['fx'],
            solver_results['fy'],
            solver_results['rx'],
            solver_results['ry'],
            solver_results['apoios'],
            solver_results['f_res'],
            bar_forces=solver_results['bar_forces']
        )

        return {
            "reactions": solver_results['reactions'],
            "equilibrium_fx": solver_results['equilibrium_fx'],
            "equilibrium_fy": solver_results['equilibrium_fy'],
            "equilibrium_ok": solver_results['equilibrium_ok'],
            "message": solver_results['message'],
            "diagram_image": diagram_base64,
            "bar_forces": solver_results['bar_forces']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)