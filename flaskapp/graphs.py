from flaskapp.auth import token_required
from flask import Blueprint, json, request, jsonify, make_response
from .graphs_utils import GraphVisualization
from . import config

graphs = Blueprint('graphs', __name__)


@graphs.route('/')
@token_required
def graphs_home(current_user):
    graph = GraphVisualization(config.NEO4J_URL, config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
    data = graph.call_d3()
    graph.close()
    #data = {'nodes': 'hello'}
    return jsonify(data)


@graphs.route('/shortest-path')
@token_required
def graphs_shortest_path(current_user):
    source_email = request.args.get('source_email')
    target_email = request.args.get('target_email')
    graph = GraphVisualization(config.NEO4J_URL, config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
    data = graph.call_shortest_path(source_email, target_email)
    graph.close()
    return jsonify(data)


@graphs.route('/label-propagation')
@token_required
def graphs_label_propagation(current_user):
    graph = GraphVisualization(config.NEO4J_URL, config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
    data = graph.call_label_propagation()
    graph.close()
    return jsonify(data)


@graphs.route('/centrality')
@token_required
def graphs_centrality(current_user):
    graph = GraphVisualization(config.NEO4J_URL, config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
    data = graph.call_centrality()
    graph.close()
    return jsonify(data)

# "MATCH (e1:Employee {emailaddress: \"ermis-f@enron.com\"}), (e2:Employee {emailaddress: \"lokey-t@enron.com\"}) "
#                         "CALL gds.beta.shortestPath.dijkstra.stream({ "
#                         "nodeQuery: 'MATCH (e:Employee) RETURN id(e) as id', "
#                         "relationshipQuery: 'MATCH (e3:Employee)-[r:EMAILS]-(e4:Employee) RETURN id(e3) as source, id(e4) as target, r.amount as weight', "
#                         "sourceNode: id(e1), "
#                         "targetNode: id(e2)}) "
#                         "YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs "
#                         "RETURN gds.util.asNode(sourceNode).emailaddress AS sourceNodeName, gds.util.asNode(targetNode).emailaddress AS targetNodeName, [nodeId IN nodeIds | nodeId] AS node_Ids, costs "
#                         "ORDER BY index"

# MATCH (e1:Employee {emailaddress: "ybarbo-p@enron.com"}), (e2:Employee {emailaddress: "pimenov-v@enron.com"}) 
# CALL example.Djikstra(e1, e2) 
# YIELD nodes,distances 
# RETURN nodes,distances