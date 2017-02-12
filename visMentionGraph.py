import networkx as nx
import re

def extractMention(data):
    return re.findall("@([a-z0-9_]+)", data.lower())

def createMentionGraph(texts, users, outFilename):
    print('Create Mention Graph start ...')
    J = nx.DiGraph()
    for text,user in zip(texts,users):
        if text:
            mentions = extractMention(text)
            for mention in mentions:
                mention = mention.lower()
                user = user.lower()
                #print mention_user, user
                if mention:
                    if not mention in J:
                        J.add_node(mention)
                    if user != "" and not user in J:
                        J.add_node(user)
                    if user != "":
                        if J.has_edge(user, mention):
                            J[user][mention]['weight'] += 1
                        else:
                            J.add_weighted_edges_from([(user, mention, 1.0)])
    
    nx.write_gexf(J, outFilename + '.gexf')
    print('Create Mention Graph end ...')
    
    return J