from fastapi import FastAPI, HTTPException
from src.scripts.pipeline import kg_pipeline_query, rag_pipeline_query
from logging_conf.logging_helpers import logger

app = FastAPI(
    title="RAG + Vanilla RAG API",
    description="An API to process user queries using a pipeline.",
    version="1.0.0",
    docs_url="/api_docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json"
)

@app.get("/healthcheck")
def healthcheck():
    logger.info("Healthcheck endpoint was called")
    return {"status": "healthy"}

@app.post("/generate_results/kg")
def process_kg_query(query: str, user_id: str):
    logger.info(f"Processing KG query for user_id: {user_id}")
    try:
        response = kg_pipeline_query(query=query, user_id=user_id)
        logger.info(f"KG query processed successfully for user_id: {user_id}")
        #sample output {
    #     "kg_response": kg_response,
    #     "retrieved_articles": retrieved_articles,
    #     "structured_kg_output": structured_kg_output
    # }
       
        return response
    except Exception as e:
        logger.error(f"Error processing KG query for user_id: {user_id}, Error: {str(e)}")
        raise HTTPException(status_code=500, detail="I am unable to process the KG response due to some error")

@app.post("/generate_results/rag")
def process_rag_query(query: str, user_id: str):
    logger.info(f"Processing RAG query for user_id: {user_id}")
    try:
        response = rag_pipeline_query(query=query, user_id=user_id)
        logger.info(f"RAG query processed successfully for user_id: {user_id}")
         # sample output - {
    #     "vanilla_response": vanilla_response,
    #     "retrieved_articles": retrieved_articles
    # }

        return response
    except Exception as e:
        logger.error(f"Error processing RAG query for user_id: {user_id}, Error: {str(e)}")
        raise HTTPException(status_code=500, detail="I am unable to process the RAG response due to some error")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI application")
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload = True)

  