from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Tuple
import math
import uvicorn

import numpy as np
from solver_core import solve_truss
from visualizer import generate_truss_diagram

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory=".")

class Node(BaseModel):
    x: float
    y: float

class Force(BaseModel):
    magnitude: float
    angle: float
    node: int

class TrussData(BaseModel):
    nodes: List[Node]
    bars: List[Tuple[int, int]]
    forces: List[Force]
    supports: Dict[int, int]

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

@app.post("/solve")
async def solve_truss_endpoint(data: TrussData):
    try:
        nodes_list = [{'x': n.x, 'y': n.y} for n in data.nodes]

        forces_list = []
        for f in data.forces:
            angle_rad = math.radians(f.angle)
            forces_list.append({
                'node': f.node,
                'fx': math.cos(angle_rad) * f.magnitude,
                'fy': math.sin(angle_rad) * f.magnitude
            })

        results = solve_truss(nodes_list, data.bars, forces_list, data.supports)

        diagram_base64 = generate_truss_diagram(
            results['coords_x'],
            results['coords_y'],
            data.bars,
            results['fx'],
            results['fy'],
            results['rx'],
            results['ry'],
            results['apoios'],
            bar_forces=results['bar_forces']
        )

        return {
            "reactions": results['reactions'],
            "equilibrium_fx": results['equilibrium_fx'],
            "equilibrium_fy": results['equilibrium_fy'],
            "equilibrium_ok": results['equilibrium_ok'],
            "message": results['message'],
            "diagram_image": diagram_base64,
            "bar_forces": results['bar_forces']
        }
    except np.linalg.LinAlgError as e:
        msg = ("Matriz de rigidez singular. A treliça não está devidamente "
               "restringida (é um mecanismo). Verifique se:\n"
               "1. Existem barras conectando todos os nós\n"
               "2. Os apoios restringem todos os movimentos de corpo rígido\n"
               "3. Não há nós desconectados da estrutura")
        raise HTTPException(status_code=400, detail=msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
