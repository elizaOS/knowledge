import asyncio
import aiosqlite
import json
import csv
import io
from aiohttp import web

class SQLiteMCP:
    def __init__(self):
        self.db = None
        self.app = web.Application()
        self.app.router.add_post('/execute_query', self.handle_execute_query)
        self.app.router.add_post('/connect', self.handle_connect)
        self.app.router.add_post('/close', self.handle_close)

    async def handle_connect(self, request):
        try:
            data = await request.json()
            db_path = data.get('database_path')
            if not db_path:
                return web.Response(status=400, text='database_path is required')
            
            if self.db:
                await self.db.close()
            
            self.db = await aiosqlite.connect(db_path)
            return web.Response(text='Connected successfully')
        except Exception as e:
            return web.Response(status=500, text=str(e))

    async def handle_close(self, request):
        if self.db:
            await self.db.close()
            self.db = None
            return web.Response(text='Connection closed')
        return web.Response(text='No active connection')

    async def handle_execute_query(self, request):
        if not self.db:
            return web.Response(status=400, text='Not connected to any database')
        
        try:
            data = await request.json()
            query = data.get('query')
            params = data.get('params', [])
            format_type = data.get('format', 'json')
            
            if not query:
                return web.Response(status=400, text='query is required')

            async with self.db.execute(query, params) as cursor:
                if query.strip().upper().startswith(('SELECT', 'PRAGMA')):
                    rows = await cursor.fetchall()
                    columns = [description[0] for description in cursor.description]
                    
                    if format_type == 'csv':
                        output = io.StringIO()
                        writer = csv.writer(output)
                        writer.writerow(columns)
                        writer.writerows(rows)
                        return web.Response(
                            text=output.getvalue(),
                            content_type='text/csv',
                            headers={'Content-Disposition': 'attachment; filename="query_result.csv"'}
                        )
                    else:
                        result = {
                            'columns': columns,
                            'rows': rows
                        }
                        return web.Response(text=json.dumps(result, default=str), content_type='application/json')
                else:
                    await self.db.commit()
                    return web.Response(text=json.dumps({'affected_rows': cursor.rowcount}))
                    
        except Exception as e:
            return web.Response(status=500, text=str(e))

    def run(self, host='localhost', port=8081):
        web.run_app(self.app, host=host, port=port)

if __name__ == '__main__':
    mcp = SQLiteMCP()
    mcp.run()
