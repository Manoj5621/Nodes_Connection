from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import networkx as nx

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request/response models
class Node(BaseModel):
    id: str
    type: str
    position: Dict[str, float]
    data: Dict[str, Any]

class Edge(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: str
    targetHandle: str

class PipelineRequest(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

class PipelineResponse(BaseModel):
    num_nodes: int
    num_edges: int
    is_dag: bool

def is_dag(nodes: List[Node], edges: List[Edge]) -> bool:
    """
    Check if the pipeline forms a Directed Acyclic Graph (DAG)
    """
    try:
        G = nx.DiGraph()
        
        # Add nodes
        for node in nodes:
            G.add_node(node.id)
        
        # Add edges
        for edge in edges:
            G.add_edge(edge.source, edge.target)
        
        # Check if graph is acyclic
        return nx.is_directed_acyclic_graph(G)
    except Exception:
        return False

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

@app.post('/pipelines/parse', response_model=PipelineResponse)
def parse_pipeline(pipeline: PipelineRequest):
    """
    Parse the pipeline and return statistics
    """
    try:
        num_nodes = len(pipeline.nodes)
        num_edges = len(pipeline.edges)
        is_dag_result = is_dag(pipeline.nodes, pipeline.edges)
        
        return PipelineResponse(
            num_nodes=num_nodes,
            num_edges=num_edges,
            is_dag=is_dag_result
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/health')
def health_check():
    return {'status': 'healthy'}