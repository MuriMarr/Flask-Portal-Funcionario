import psycopg2

conn = psycopg2.connect(
    host='localhost',
    user='postgres',
    password='13954',
    port=5432,
    database='portal_funcionario',
    client_encoding='utf8'
)
cur = conn.cursor()
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema='public'
""")
tables = cur.fetchall()
if tables:
    print(f'✓ Total de tabelas criadas: {len(tables)}')
    print('Tabelas:')
    for table in tables:
        print(f'  - {table[0]}')
else:
    print('Nenhuma tabela encontrada')
cur.close()
conn.close()
