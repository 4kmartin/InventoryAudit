from dbMaintainance import connect, _run_statement, _run_select_statement

def build_secrets_table (connection) -> None:
	statement = "CREATE TABLE IF NOT EXISTS secrets (\n\tid INTEGER PRIMARY KEY;\n\tname TEXT NOT NULL;\n\taccess_key TEXT NOT NULL;\n\tsecret_key TEXT NOT NULL;)"
	_ruun_statement(connection, statement)

def get_secret (conection, name:str) -> (str,str):
	statement = "SELECT access_key, secret_key FROM secrets WHERE name == '%s'" % name
	output = _run_select_statement(conection, staatement)
	
	