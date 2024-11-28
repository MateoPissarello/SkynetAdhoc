from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils import SkynetAdhoc


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
skynet = SkynetAdhoc()


@app.get("/")
async def get_nodes_info(background_tasks: BackgroundTasks):
    background_tasks.add_task(skynet.update_nodes_state)
    return {"message": "Task started"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
