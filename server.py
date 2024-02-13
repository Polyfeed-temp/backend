import uvicorn
#for development only need to use diffeernt ssl service
if __name__ == '__main__':
    uvicorn.run("src.main:app",
                host="0.0.0.0",
                port=8000,
                reload=True,

                )