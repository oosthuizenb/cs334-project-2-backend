from neo4j import GraphDatabase

class GraphVisualization:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def call_create_graph(self):
        with self.driver.session() as session:
            session.write_transaction(self._create_graph)

    def call_d3(self):
        with self.driver.session() as session:
            d3_dict = session.write_transaction(self._format_to_d3)
        return d3_dict

    def call_label_propagation(self):
        with self.driver.session() as session:
            data = session.write_transaction(self._label_propagation)
        return data

    def call_shortest_path(self, source_email, target_email):
        with self.driver.session() as session:
            data = session.write_transaction(self._shortest_path, source_email, target_email)
        return data

    def call_centrality(self):
        with self.driver.session() as session:
            data = session.write_transaction(self._centrality)
        return data

    @staticmethod
    def _create_graph(tx):
        result = tx.run("LOAD CSV WITH HEADERS FROM \"https://docs.google.com/spreadsheets/d/e/2PACX-1vShL6tSPb9FxtCl2du9JlC67dYxThalN0qQiogVshCAxeW5ZumevUeZQwDLX06XHD-GYsBT4CVFXwCO/pub?gid=1827418886&single=true&output=csv\" AS row "
                        "CREATE (e:Employee {emailaddress: row.emailaddress}) ")
        result = tx.run("LOAD CSV WITH HEADERS FROM \"https://docs.google.com/spreadsheets/d/e/2PACX-1vTpHPhmBsnf-pPXP7t4O6fBBnC4Aff0pozq2VDbG9A5Ami8AwVt0hzpw-P3lDJfa_kUV5ZL_HTcPpmE/pub?gid=1232337158&single=true&output=csv\" AS row "
                        "CREATE (m:Message {mid: row.mid, sender: row.sender}) ")

        result = tx.run("LOAD CSV WITH HEADERS FROM \"https://docs.google.com/spreadsheets/d/e/2PACX-1vQ7GTYjmsURZDthaPJRjMcjnoSgZMWtH8F6xBIjgr7aTL09QOKE8BkC44VS-GSBUGBF58C6aHy5S78o/pub?gid=588837195&single=true&output=csv\" AS row "
                        "CREATE (r:Recipient {mid: row.mid, rvalue: row.emailaddress}) ")

        

    @staticmethod
    def _format_to_d3(tx):
        result = tx.run("MATCH (e1:Employee)-[r:EMAILS]->(e2:Employee) "
                        "WHERE (e1)-[:SENT]->(e2) AND (e2)-[:SENT]->(e1) "
                        "RETURN e1, e2, r ")

        nodes = []
        links = []
        for record in result:
            node_1 = {
                'id': record['e1']._id,
                'firstname': record['e1']._properties['firstname'],
                'lastname': record['e1']._properties['lastname'],
                'emailaddress': record['e1']._properties['emailaddress'],
            }
            node_2 = {
                'id': record['e2']._id,
                'firstname': record['e2']._properties['firstname'],
                'lastname': record['e2']._properties['lastname'],
                'emailaddress': record['e2']._properties['emailaddress'],
            }
            link = {
                'source': record['r'].nodes[0]._id,
                'target': record['r'].nodes[1]._id,
            }
            if node_1 not in nodes:
                nodes.append(node_1)
            if node_2 not in nodes:
                nodes.append(node_2)
            if link not in links:
                links.append(link)

        d3_dict = {
            'nodes': nodes,
            'links': links,
        }
        return d3_dict

    @staticmethod
    def _label_propagation(tx):
        result_1 = tx.run(
                        "CALL gds.labelPropagation.stream({ "
                        "nodeProjection: 'Employee', "
                        "relationshipProjection: 'SENT', "
                        "relationshipProperties: 'amount'"
                        "}) ")
        
        communities = {}

        for record in result_1:
            communities[str(record['nodeId'])] = record['communityId']

        result_2 = tx.run("MATCH (e1:Employee)-[r:SENT]->(e2:Employee) "
                        "RETURN e1, e2, r ")
        nodes = []
        links = []
        for record in result_2:
            node_1 = {
                'id': record['e1']._id,
                'emailaddress': record['e1']._properties['emailaddress'],
                'communityId': communities[str(record['e1']._id)],
            }
            node_2 = {
                'id': record['e2']._id,
                'emailaddress': record['e2']._properties['emailaddress'],
                'communityId': communities[str(record['e2']._id)],
            }
            link = {
                'source': record['r'].nodes[0]._id,
                'target': record['r'].nodes[1]._id,
            }
            if node_1 not in nodes:
                nodes.append(node_1)
            if node_2 not in nodes:
                nodes.append(node_2)
            if link not in links:
                links.append(link)

        d3_dict = {
            'nodes': nodes,
            'links': links,
        }
        return d3_dict  

    @staticmethod
    def _shortest_path(tx, source_email, target_email):
        # print(source_email)
        source = '"solberg-g@enron.com"'
        target = '"lokey-t@enron.com"'
        if source_email:
            source = f'"{source_email}"'
        if target_email:
            target = f'"{target_email}"'
        result_1 = tx.run(
                        "MATCH (e1:Employee {emailaddress: " + source + "}), (e2:Employee {emailaddress: " + target + "}) "
                        "CALL gds.beta.shortestPath.dijkstra.stream({ "
                        "nodeQuery: 'MATCH (e:Employee) RETURN id(e) as id', "
                        "relationshipQuery: 'MATCH (e3:Employee)-[r:BI]-(e4:Employee) WHERE r.amount > 4 RETURN id(e3) as source, id(e4) as target, r.amount as weight', "
                        "sourceNode: id(e1), "
                        "targetNode: id(e2)}) "
                        "YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs "
                        "RETURN gds.util.asNode(sourceNode).emailaddress AS sourceNodeName, gds.util.asNode(targetNode).emailaddress AS targetNodeName, [nodeId IN nodeIds | nodeId] AS node_Ids, costs "
                        "ORDER BY index")
        
        path_nodes = []

        for record in result_1:
            for node_id in record['node_Ids']:
                path_nodes.append(node_id)

        result_2 = tx.run("MATCH (e1:Employee)-[r:SENT]->(e2:Employee) "
                        "RETURN e1, e2, r ")
        nodes = []
        links = []
        for record in result_2:
            node_1 = {
                'id': record['e1']._id,
                'emailaddress': record['e1']._properties['emailaddress'],
            }
            node_2 = {
                'id': record['e2']._id,
                'emailaddress': record['e2']._properties['emailaddress'],
            }
            link = {
                'source': record['r'].nodes[0]._id,
                'target': record['r'].nodes[1]._id,
            }
            if node_1 not in nodes:
                nodes.append(node_1)
            if node_2 not in nodes:
                nodes.append(node_2)
            if link not in links:
                links.append(link)

        d3_dict = {
            'nodes': nodes,
            'links': links,
            'path_nodes': path_nodes,
        }
        return d3_dict     

    @staticmethod
    def _centrality(tx):
        result_1 = tx.run(
                        "CALL gds.pageRank.stream({"
                        "nodeProjection: 'Employee', "
                        "relationshipProjection: 'SENT', "
                        "relationshipProperties: 'amount', "
                        "relationshipWeightProperty: 'amount'}) "
                        "YIELD nodeId, score "
                        "RETURN nodeId AS id, score "
                        "ORDER BY score DESC, id ASC")
        
        node_scores = {}

        for record in result_1:
            node_scores[str(record['id'])] = record['score']

        result_2 = tx.run("MATCH (e1:Employee)-[r:SENT]->(e2:Employee) "
                        "RETURN e1, e2, r ")
        nodes = []
        links = []
        for record in result_2:
            node_1 = {
                'id': record['e1']._id,
                'emailaddress': record['e1']._properties['emailaddress'],
                'score': node_scores[str(record['e1']._id)],
            }
            node_2 = {
                'id': record['e2']._id,
                'emailaddress': record['e2']._properties['emailaddress'],
                'score': node_scores[str(record['e2']._id)],
            }
            link = {
                'source': record['r'].nodes[0]._id,
                'target': record['r'].nodes[1]._id,
            }
            if node_1 not in nodes:
                nodes.append(node_1)
            if node_2 not in nodes:
                nodes.append(node_2)
            if link not in links:
                links.append(link)

        d3_dict = {
            'nodes': nodes,
            'links': links,
        }
        return d3_dict  


