import os
from fastapi import FastAPI, Request, HTTPException
import httpx

app = FastAPI()

TOKEN_CREATION_ENDPOINT = "http://127.0.0.1:8069/api/auth/"
ODOO_AUTH_ENDPOINT = "http://127.0.0.1:8069/web/session/authenticate"
DB = os.getenv("DB")
LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")

credentials_odoo = {
    "jsonrpc": "2.0",
    "params": {
        "db": DB,
        "login": LOGIN,
        "password": PASSWORD
    }
}

@app.post("/api/authentication/")
async def authentication(request: Request):

	credentials = await request.json()

	async with httpx.AsyncClient() as client:
		token_response = await client.post(TOKEN_CREATION_ENDPOINT, json=credentials)

		if token_response.status_code == 404:
			odoo_response = await client.post(ODOO_AUTH_ENDPOINT, json=credentials_odoo)
			if odoo_response.status_code != 200:
				raise HTTPException(
					status_code=odoo_response.status_code,
					detail="A autenticação da Api do sistema falhou."
				)
			# Após autenticar com sucesso no Odoo, refaz a chamada para obter o token.
			token_response = await client.post(TOKEN_CREATION_ENDPOINT, json=credentials)

		if token_response.status_code != 200:
			# Se mesmo após as tentativas o token não for criado, retorna o erro para o cliente.
			raise HTTPException(
				status_code=token_response.status_code,
				detail="A criação do token falhou."
			)

		return token_response.json()


if __name__ == "__main__":
	import uvicorn

	uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
