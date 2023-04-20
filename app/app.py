#./app/app.py

from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from flask_restful import Api, Resource, reqparse
from pymongo import MongoClient
from users import *

app = Flask(__name__)
app.secret_key='this-is-a-very-secret-key'

client = MongoClient("mongo", 27017) # Connect to mongo service (docker) at the standard port
db = client.SampleCollections        # Sample database

# Main page
@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/pokemon', methods=['GET','POST'])
def pokemon(): # Pokemon database search    
    if request.method == 'POST':
        if 'name' in request.form:
            pokemons=db.samples_pokemon.find({'name':{"$regex":request.form['name'],"$options":'i'}}).sort('id')
        elif 'num' in request.form:
            n=request.form['num']
            if len(n)<3:
                n='0'*(3-len(n))+n
            pokemons=db.samples_pokemon.find({'num':n}).sort('id')
        elif 'type' in request.form:
            pokemons=db.samples_pokemon.find({'type':{"$regex":request.form['type'],"$options":'i'}}).sort('id')
    else:
        pokemons=db.samples_pokemon.find().sort('id')
        
    pokemon_list = [{k:p[k] for k in ("num","name","img","type","prev_evolution","next_evolution") if k in p} for p in pokemons]
    
    return render_template('pokemon.html',n=len(pokemon_list),pkmlist=pokemon_list)

@app.route('/pokemon/adv', methods=['POST'])
def pokemon_adv(): # Pokemon advanced search
    pokemons=db.samples_pokemon.find({'name':{"$regex":request.form['name'],"$options":'i'}, 'type':{"$regex":request.form['type'],"$options":'i'}}).sort('id')
        
    pokemon_list = [{k:p[k] for k in ("num","name","img","type","prev_evolution","next_evolution") if k in p} for p in pokemons]
    
    return render_template('pokemon.html',n=len(pokemon_list),pkmlist=pokemon_list)

def stripList(l): # List from string
    l=l.replace('[','').replace(']','').replace(' ','').replace("'","")
    return l.split(',')

def stripDictList(l): # List of dicts from string
    l=l.replace('[','').replace(']','').replace('{','').replace('}','')
    l=l.replace("'num'",'').replace("'name'",'')
    l=l.replace(' ','').replace(':','').replace("'","")
    l=l.split(',')
    result=[]
    for i in range(0,len(l)-1,2):
        result.append({'num':l[i], 'name':l[i+1]})
    return result

@app.route('/pokemon/edit/<num>', methods=['GET','POST'])
def editPkmn(num):

    if request.method=='POST':
        n=request.form['num']
        if len(n)<3:
                n='0'*(3-len(n))+n
        name=request.form['name']
        img=request.form['img']
        typ=stripList(request.form['type'])
        prev=stripDictList(request.form['prev'])
        nex=stripDictList(request.form['next'])
        # The pokedex numbers must be unique
        if num==n or db.samples_pokemon.count_documents({'id':int(n)})==0:
            db.samples_pokemon.find_one_and_update({'id':int(num)},
                                                   {'$set':{'name':name,
                                                   'id':int(n), 'img':img,
                                                   'num':n, 'type':typ,
                                                   'prev_evolution':prev,
                                                   'next_evolution':nex}})
            flash('Pokemon data modified successfully.')
            return redirect('/pokemon/edit/'+n)
        else:
            flash('Data not modified. There exists already a Pokemon with such number :(')
        return redirect('/pokemon/edit/'+num)

    pok=db.samples_pokemon.find({'num':num})
    for p in pok:
        pok={k:p[k] for k in ("num","name","img","type","prev_evolution","next_evolution") if k in p}
    
    return render_template('editPkmn.html', pok=pok)

@app.route('/pokemon/add', methods=['GET','POST'])
def addPkmn():
    if request.method=='POST':
        n=request.form['num']
        if len(n)<3:
                n='0'*(3-len(n))+n
        name=request.form['name']
        img=request.form['img']
        typ=stripList(request.form['type'])
        prev=stripDictList(request.form['prev'])
        nex=stripDictList(request.form['next'])
        # The pokedex numbers must be unique
        if db.samples_pokemon.count_documents({'id':int(n)})==0:
            db.samples_pokemon.insert_one({'name':name,'id':int(n), 'img':img,
                                                   'num':n, 'type':typ,
                                                   'prev_evolution':prev,
                                                   'next_evolution':nex})
            flash('Pokemon added successfully.')
            return redirect('/pokemon/edit/'+n)
        else:
            flash('Data not modified. There exists already a Pokemon with such number :(')
        
    return render_template('addPkmn.html')


@app.route('/pokemon/delete/<num>')
def deletePkmn(num):
    db.samples_pokemon.delete_one({'num':num})
    flash('Pokemon deleted successfully.')
    return redirect(url_for('home'))
    
# URL not defined
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Stats page: Number of Pokemon of each type
@app.route('/stats-type')
def statsType():
    data={}
    types=db.samples_pokemon.distinct("type") # List of types
    for t in types:
        data[t]=db.samples_pokemon.count_documents({"type":t}) # Number of Pokemon of each type
    return render_template('stats-type.html', types=list(data.keys()), counts=list(data.values()))

# Stats page: Percentage of Pokemon in each evolutionary stage
@app.route('/stats-evol')
def statsEvol():
    count=[0]*3
    count[1]=db.samples_pokemon.count_documents({"prev_evolution":{ "$exists": True, "$size": 1}}) # Have evolved once
    count[2]=db.samples_pokemon.count_documents({"prev_evolution":{ "$exists": True, "$size": 2}}) # Have evolved twice
    count[0]=db.samples_pokemon.count_documents({"prev_evolution":{ "$exists": False}}) # Have never evolved
    count[0]+=db.samples_pokemon.count_documents({"prev_evolution":{ "$exists": True, "$size": 0}})
    return render_template('stats-evol.html', count=count)

# Interactive maps
@app.route('/map-markers')
def mapMarkers():
    return render_template('map-markers.html')

@app.route('/map-explore')
def mapExplore():
    return render_template('map-explore.html')

##############
#  REST API  #
##############

@app.route('/api/pokemon', methods=['GET','POST'])
def api_search_add():

    if request.method == 'GET': # Search in the database
        args=request.args

        name=''
        typ=''

        if 'num' in args: # If you search by a number, you get that pokemon
            n=args['num']
            if len(n)<3:
                n='0'*(3-len(n))+n
            pokemons=db.samples_pokemon.find({'num':n}).sort('id')
        else: # Otherwise, it searches by name and type
            if 'name' in args:
                name=args['name']
            if 'type' in args:
                typ=args['type']

            pokemons=db.samples_pokemon.find({'name':{"$regex":name,"$options":'i'}, 'type':{"$regex":typ,"$options":'i'}}).sort('id')

        pokemon_list = [{k:p[k] for k in ("num","name","img","type","prev_evolution","next_evolution") if k in p} for p in pokemons]
        return jsonify(pokemon_list)

    if request.method == 'POST': # Add a Pokemon
        args=request.json

        n=args['num']
        if len(n)<3:
            n='0'*(3-len(n))+n
        args['num']=n
        if db.samples_pokemon.count_documents({'id':int(n)})==0:
            db.samples_pokemon.insert_one(args)
            del args['_id']
            return jsonify(args)

        else:
            return jsonify({'error':'A Pokemon with such number already exists'})

@app.route('/api/pokemon/<id>', methods=['GET','PUT','DELETE'])
def api_edit_delete(id):

    if request.method == 'GET': # Search one Pokemon by number
        try:
            if len(id)<3:
                id='0'*(3-len(id))+id
            pkmn = db.samples_pokemon.find_one({'id': int(id)})
            pkmn={k:pkmn[k] for k in ("num","name","img","type","prev_evolution","next_evolution") if k in pkmn}
            pkmn['id']=int(id)
            return jsonify(pkmn)
        except:
            return jsonify({'error':'Not found'}), 404

    if request.method == 'DELETE': # Delete Pokemon
        if db.samples_pokemon.count_documents({'id':int(id)})==0:
            return jsonify({'error':'Not found'}), 404
        db.samples_pokemon.delete_one({'id':int(id)})
        return jsonify({'id':int(id)})

    if request.method == 'PUT': # Edit a Pokemon
        if db.samples_pokemon.count_documents({'id':int(id)})==0:
            return jsonify({'error':'Not found'}), 404
        args=request.json
        n=id
        if 'num' in args:
            n=int(args['num'])
            if n != int(id) and db.samples_pokemon.count_documents({'id':n})>0:
                return jsonify({'error':'A Pokemon with such id already exists'})
            args['id']=n
        db.samples_pokemon.find_one_and_update({'id':int(id)},{'$set':args})
        id=n
        return redirect('/api/pokemon/'+str(id))   

#################################
#  REST API with FLASK-RESTFULL #
#################################

api = Api(app)

pokemon_get_args=reqparse.RequestParser()
pokemon_get_args.add_argument("name", type=str)
pokemon_get_args.add_argument("type", type=str)
pokemon_get_args.add_argument("num", type=str)

class Pkmns(Resource):

    def get(self): # Search in the database
        args=pokemon_get_args.parse_args()
        name=''
        typ=''

        if args['num']!=None: # If you search by a number, you get that pokemon
            n=args['num']
            if len(n)<3:
                n='0'*(3-len(n))+n
            pokemons=db.samples_pokemon.find({'num':n}).sort('id')
        else: # # Otherwise, it searches by name and type
            if args['name']!=None:
                name=args['name']
            if args['type']!=None:
                typ=args['type']

            pokemons=db.samples_pokemon.find({'name':{"$regex":name,"$options":'i'}, 'type':{"$regex":typ,"$options":'i'}}).sort('id')

        pokemon_list = [{k:p[k] for k in ("num","name","img","type","prev_evolution","next_evolution") if k in p} for p in pokemons]
        return jsonify(pokemon_list)

    def post(self): # Add a Pokemon
        args=request.json

        n=args['num']
        if len(n)<3:
            n='0'*(3-len(n))+n
        args['num']=n
        if db.samples_pokemon.count_documents({'id':int(n)})==0:
            args['id']=int(n)
            db.samples_pokemon.insert_one(args)
            del args['_id']
            return jsonify(args)

        else:
            return jsonify({'error':'A Pokemon with such number already exists'})

class Pkmn(Resource):

    def get(self, id): # Search one Pokemon by number
        try:
            pkmn = db.samples_pokemon.find_one({'id': int(id)})
            pkmn={k:pkmn[k] for k in ("num","name","img","type","prev_evolution","next_evolution") if k in pkmn}
            pkmn['id']=int(id)
            return jsonify(pkmn)
        except:
            return {'error':'Not found'}, 404

    def delete(self, id): # Delete Pokemon
        if db.samples_pokemon.count_documents({'id':int(id)})==0:
            return {'error':'Not found'}, 404
        db.samples_pokemon.delete_one({'id':int(id)})
        return jsonify({'id':int(id)})

    def put(self, id): # Edit a Pokemon
        if db.samples_pokemon.count_documents({'id':int(id)})==0:
            return {'error':'Not found'}, 404
        args=request.json
        n=id
        if 'num' in args:
            n=int(args['num'])
            if n != int(id) and db.samples_pokemon.count_documents({'id':n})>0:
                return jsonify({'error':'A Pokemon with such id already exists'})
            args['id']=n
        db.samples_pokemon.find_one_and_update({'id':int(id)},{'$set':args})
        id=n
        return redirect('/api/pokemon/'+str(id))

api.add_resource(Pkmn, "/api2/pokemon/<id>")
api.add_resource(Pkmns, "/api2/pokemon")

###################
# User management #
###################

# Login
@app.route('/login', methods=['POST'])
def login():
    user = request.form['user']
    passwd = request.form['passwd']
    
    if checkUser(user):
        if passwd == getUser(user)['passwd']:
            session['user']=user
            session['urls'] = []
            session['names']= []
            flash(user+' logged in successfully :D')
        else:
            flash('Incorrect password :(')
    else:
        flash('User not registered :(')

    return redirect(url_for('home'))

# Sign Up
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user = request.form['user']
        passwd = request.form['passwd']
        color = request.form['color']
        if not checkUser(user):          
            session['user']=user
            session['urls'] = []
            session['names']= []
            addUser(user,{'passwd':passwd, 'color':color})
            flash(user+' successfully signed up :D')
        else:
            flash(user+' is already registered >:(')
        return redirect(url_for('home'))

    return render_template('signup.html')

@app.route('/logout') # Log out
def logout():
    flash('Good bye '+session['user']+'!')
    session['user']=''
    return redirect(url_for('home'))

@app.route('/user') # User info and options
def user():
    return render_template('user.html', user=getUser(session['user']))

@app.route('/change', methods=['GET','POST']) # Change user data
def change():
    if request.method == 'POST':
        user = request.form['user']
        passwd = request.form['passwd']
        color = request.form['color']

        if user == session['user'] or not checkUser(user):
            delUser(session['user']) # Delete old user
            addUser(user,{'passwd':passwd, 'color':color}) # Add new user
            session['user']=user
            flash('Changes performed successfully :)')
            return redirect(url_for('home'))
        else:
            flash(user+' is already registered, the changes were not saved >:(')
            return redirect(url_for('change'))
        
    return render_template('change.html', user=getUser(session['user']))

@app.route('/delete')
def delete():
    delUser(session['user'])
    flash('User '+session['user']+' has been deleted')
    session['user']=''
    return redirect(url_for('home'))

if __name__=='__main__':
    app.run(debug=False, host="0.0.0.0", port=5000)