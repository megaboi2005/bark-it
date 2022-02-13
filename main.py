from aiohttp import web
from os.path import exists
from cryptography.fernet import Fernet






    


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
		finalname = filter(name)
		finalpass = str(f.encrypt(filter(password).encode()))
		users = open('users/users.json','r').read()
		#{"Name":"bob", "Password":"5d41402abc4b2a76b9719d911017c592", "Email":"bob@email.com", "Posts":[2, 32, 53, 74]}
		output = '{"'+ finalname +':{password":"' + finalpass + '"}}'+'\n'
		if name in users:
			return web.Response(text='account exists',content_type='text/html')
		else:
			userwrite = open('users/users.json','a')
			userwrite.write(output)
			return web.Response(text='yay',content_type='text/html')
		return web.Response(text='something went wrong sorry',content_type='text/html')
	except KeyError:
		formin = form('name','pass','register')
		return web.Response(text=formin,content_type='text/html')


if not exists('secret.key'):
	key = Fernet.generate_key()
	key_file = open("secret.key", "wb")
	key_file.write(key)
else:
	key = open("secret.key", "rb").read()
	print(key)
f = Fernet(key)


app = web.Application()
app.add_routes([
                web.get('/register', register),
                
                ])


web.run_app(app)