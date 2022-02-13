from aiohttp import web


def form(name,desc,location):
	form = open('elements/form.txt','r')
	formout = form.read()
	return formout.replace('{name}',name).replace('{location}',location).replace('{desc}',desc)

def filter(var):
	output = var.replace('"','\"').replace('<',' &lt').replace('>','&gt;').replace('</textarea>','(nice try)').replace("'",'\'')
	return output

async def register(request):
	try:
		name = request.rel_url.query['name']
		password = request.rel_url.query['pass']
		finalname = {filter(name)}
		finalpass = filter(password)
		output = '{"name":"'+finalname+'","post":"'+finalpass+'"}'
		return web.Response(text='yay',content_type='text/html')
	
	except KeyError:
		formin = form('name','pass','register')
		return web.Response(text=formin,content_type='text/html')







app = web.Application()
app.add_routes([
                web.get('/register', register),
                
                ])


web.run_app(app)