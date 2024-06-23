import uvicorn
#for development only need to use diffeernt ssl service
if __name__ == '__main__':
    uvicorn.run(
                "src.main:app",
                host="0.0.0.0",
                # dev = 8000, production = 8002
                port=8002,
                reload=True
            )