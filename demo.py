# -*- coding: utf-8 -*-
"""
Created on Sat Dec 16 20:47:18 2017

@author: gf_admin
"""
from flask import Flask, request, render_template, g, jsonify
import sqlite3
import datetime, time
from block_chain_uppsala_v4 import Blockchain
from uuid import uuid4

app = Flask(__name__)
    
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def query_db(query, args=()):
    
    cur = get_db().cursor()
    cur.execute(query, args)
    #cur.executemany(query, args)
    
    #rv = cur.fetchmany() #Retrive 1 row
    rv = cur.fetchall()   #Retrive all rows
    cur.close()
    return rv
    #return (rv[0] if rv else None) if one else rv

def update_db(query, args=(), one=False):
    conn = get_db()
    conn.execute(query, args)
    conn.commit()
    conn.close()
    return "DB updated"

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/") # take note of this decorator syntax, it's a common pattern
def home():
    return render_template('home.html')

@app.route('/report', methods=['GET', 'POST'])
def report_screen():
    return render_template('report_case.html')

@app.route('/raise_case', methods=['GET', 'POST'])
def raise_case():
    
    cat = request.form.get('OPTION1')
    currtype = request.form.get('OPTION2')
    domain = request.form.get('DOMAIN')
    ipadr = request.form.get('IPADR')
    url = request.form.get('URL')
    hash_value = request.form.get('HASH')
    walletadr = request.form.get('WALLETADR')
    title = request.form.get('TITLE')
    desc = request.form.get('DESC')

    rpt_time = datetime.datetime.now()
    case_id = int(time.mktime(rpt_time.timetuple()))
    status = 'Confirmed'
    
    user = 'User_1'
    user_email = 'guofeng20094@gmail.com'
    
    tmp_list = [case_id, cat, currtype, domain, ipadr, url, hash_value, 
                walletadr, title, desc, rpt_time, status, user, user_email]
    
    update_db("INSERT INTO TB_CASE (CASE_ID, CATEGORY, CURR_TYPE, DOMAIN, \
                                   IPADR, URL, HASH_VALUE, WALLETADR, TITTLE, \
                                   DESC, RPTTIME, STATUS, USER, EMAIL) \
   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?);", tmp_list)

    return "Case Raised with case ID: "+str(case_id)

@app.route('/search_case', methods=['GET', 'POST'])
def search_case():
    
    search_value = request.form.get('S_VALUE')
       
    tmp_list = [search_value]
         
    rows = query_db("SELECT * from TB_CASE WHERE CASE_ID = ?", tmp_list)
    
    if not rows:
        rows = query_db("SELECT * from TB_CASE WHERE IPADR = ?", tmp_list)
        
    if not rows:
        rows = query_db("SELECT * from TB_CASE WHERE WALLETADR = ?", tmp_list)

    if not rows:
        rows = query_db("SELECT * from TB_CASE WHERE DOMAIN = ?", tmp_list)

    if not rows:
        rows = query_db("SELECT * from TB_CASE WHERE URL = ?", tmp_list)
    
    return render_template('case_results.html', result=rows)

def initial_load() :
    
    
    
    
    
    pass
    # Instantiate the Node

"""
Below code is on the blockchain functions
"""



@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
        confirmed_cases = []
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    #return jsonify(response), 200

    return response['message']


@app.route('/transactions/new', methods=['GET', 'POST'])
def new_transaction():
    #values = request.get_json()
    
    tmp_list = ['Confirmed']
    #Retrive the confirmed cases from database and insert to transaction
    rows = query_db("SELECT * from TB_CASE WHERE STATUS = ?", tmp_list)
    
    cases_ctr = len(rows)
    values = {'sender': '0', 'recipient': 'Node1', 'amount': cases_ctr*10, 'confirmed_cases': rows}
    

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount', 'confirmed_cases']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], 
                                       values['amount'], values['confirmed_cases'])


    tmp_list = ['BlockChained', 'Confirmed']
    update_db("UPDATE TB_CASE SET STATUS = ? WHERE STATUS = ?", tmp_list)

    response = {'message': f'{cases_ctr} Transactions will be added to Block {index}'}
      
    #return jsonify(response), 201
    return response['message']

@app.route('/transactions/new_ether', methods=['GET', 'POST'])
def new_transaction_ether():
    #values = request.get_json()
    
    cases = query_db("SELECT * from etherscamdb")
    
    cases_ctr = len(cases)
    
    for case in cases:
        values = {'sender': '0', 'recipient': 'Node1', 'amount': 1, 'confirmed_cases': case}
        
    #    # Check that the required fields are in the POST'ed data
        required = ['sender', 'recipient', 'amount', 'confirmed_cases']
        if not all(k in values for k in required):
            return 'Missing values', 400
    
        # Create a new Transaction
        index = blockchain.new_transaction(values['sender'], values['recipient'], 
                                           values['amount'], values['confirmed_cases'])
#
#
#    tmp_list = ['BlockChained', 'Confirmed']
#    update_db("UPDATE TB_CASE SET STATUS = ? WHERE STATUS = ?", tmp_list)

    response = {'message': f'{cases_ctr} Transactions will be added to Block {index}'}
      
    #return jsonify(response), 201
    return response['message']


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    #return jsonify(response), 200

    tmp = response['chain']
    return " ".join(str(x) for x in tmp)

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    #values = request.get_json()

    values = {'nodes', 'http://192.168.0.5:5000'}

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    
    #return jsonify(response), 201
    tmp = response['total_nodes']
    return " ".join(str(x) for x in tmp)


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    #return jsonify(response), 200

    return response['message']


    
if __name__ == '__main__':
        
    DATABASE = "C:\\uppsala\demo.db"
    
    # Generate a globally unique address for this node
    node_identifier = str(uuid4()).replace('-', '')
    
    # Instantiate the Blockchain
    blockchain = Blockchain()    
    #Load the block chain into memeory    
    
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5001, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    
    initial_load() 
    app.run(host= '0.0.0.0', port=port, debug=True)