#
# License: BSD
#   https://raw.github.com/robotics-in-concert/rocon_qt_gui/license/LICENSE
#
##############################################################################
# Imports
##############################################################################

import re
import copy
import rocon_gateway_utils
import rosgraph.impl.graph
from rosgraph.impl.graph import Edge, EdgeList
import roslib
import concert_msgs.msg as concert_msgs

import rospy

##############################################################################
# Implementation
##############################################################################


def matches_any(name, patternlist):
    if patternlist is None or len(patternlist) == 0:
        return False
    for pattern in patternlist:
        if str(name).strip() == pattern:
            return True
        if re.match("^[a-zA-Z0-9_/]+$", pattern) is None:
            if re.match(str(pattern), name.strip()) is not None:
                return True
    return False


class NodeConnections:
    def __init__(self, incoming=None, outgoing=None):
        self.incoming = incoming or []
        self.outgoing = outgoing or []


class ConductorGraphDotcodeGenerator:

    def __init__(self):
        pass

    def _add_edge(self, edge, dotcode_factory, dotgraph):
#         if is_topic:
#             dotcode_factory.add_edge_to_graph(dotgraph, edge.start, edge.end, label=edge.label, url='topic:%s' % edge.label)
#         else:
        dotcode_factory.add_edge_to_graph(dotgraph, edge.start, edge.end, label=edge.label)

    def _add_conductor_node(self, dotcode_factory, dotgraph):
        '''
        The conductor is a special case node, we treat this especially here.
        '''
        dotcode_factory.add_node_to_graph(dotgraph,
                                          nodename="conductor",
                                          #nodename=rocon_gateway_utils.gateway_basename(node),
                                          #nodelabel=rocon_gateway_utils.gateway_basename(node),
                                          shape='ellipse',
                                          url="conductor",
                                          #url=node
                                          color="blue"
                                          )

    def _add_node(self, node, dotcode_factory, dotgraph):
        '''
        A node here is a concert client. We basically add nodes and classify according
        to their state in the dotgraph.

        :param node .concert_client.ConcertClient: the concert client to show on the dotgraph
        '''
        # colour strings defined as per http://qt-project.org/doc/qt-4.8/qcolor.html#setNamedColor
        # and http://www.w3.org/TR/SVG/types.html#ColorKeywords
        if node.state == concert_msgs.ConcertClientState.PENDING:
            node_colour = "fuschia"
        elif node.state == concert_msgs.ConcertClientState.JOINING:
            node_colour = "fuschia"
        elif node.state == concert_msgs.ConcertClientState.UNINVITED:
            node_colour = "midnightblue"
        elif node.state == concert_msgs.ConcertClientState.AVAILABLE:
            node_colour = "blue"
        elif node.state == concert_msgs.ConcertClientState.MISSING:
            node_colour = "powderblue"
        elif node.state == concert_msgs.ConcertClientState.BLOCKING:
            node_colour = "black"
        elif node.state == concert_msgs.ConcertClientState.BUSY:
            node_colour = "black"
        elif node.state == concert_msgs.ConcertClientState.GONE:
            node_colour = "black"
        dotcode_factory.add_node_to_graph(dotgraph,
                                          nodename=node.concert_alias,
                                          #nodename=rocon_gateway_utils.gateway_basename(node),
                                          #nodelabel=rocon_gateway_utils.gateway_basename(node),
                                          shape='ellipse',
                                          url=rocon_gateway_utils.gateway_basename(node.gateway_name),
                                          #url=node,
                                          color=node_colour
                                          )

#     def _add_topic_node(self, node, dotcode_factory, dotgraph):
#         label = rosgraph.impl.graph.node_topic(node)
#         dotcode_factory.add_node_to_graph(dotgraph,
#                                           nodename=label,
#                                           nodelabel=label,
#                                           shape='box',
#                                           url="topic:%s" % label)
#
#     def generate_namespaces(self, graph, graph_mode):
#         """
#         Determine the namespaces of the nodes being displayed
#         """
#         nodes = graph.gateway_nodes
#         namespaces = list(set([roslib.names.namespace(n) for n in nodes]))
#         return list(set(namespaces))
#
#     def _filter_orphaned_edges(self, edges, nodes):
#         nodenames = [str(n).strip() for n in nodes]
#         # currently using and rule as the or rule generates orphan nodes with the current logic
#         return [e for e in edges if e.start.strip() in nodenames and e.end.strip() in nodenames]
#
#     def _filter_orphaned_topics(self, connection_nodes, edges):
#         '''remove topic graphnodes without connected ROS nodes'''
#         removal_nodes = []
#         for n in connection_nodes:
#             keep = False
#             for e in edges:
#                 if (e.start.strip() == str(n).strip() or e.end.strip() == str(n).strip()):
#                     keep = True
#                     break
#             if not keep:
#                 removal_nodes.append(n)
#         for n in removal_nodes:
#             connection_nodes.remove(n)
#         return connection_nodes

    def _split_filter_string(self, ns_filter):
        '''splits a string after each comma, and treats tokens with leading dash as exclusions.
        Adds .* as inclusion if no other inclusion option was given'''
        includes = []
        excludes = []
        for name in ns_filter.split(','):
            if name.strip().startswith('-'):
                excludes.append(name.strip()[1:])
            else:
                includes.append(name.strip())
        if includes == [] or includes == ['/'] or includes == ['']:
            includes = ['.*']
        return includes, excludes

    def _get_node_edge_map(self, edges):
        '''returns a dict mapping node name to edge objects partitioned in incoming and outgoing edges'''
        node_connections = {}
        for edge in edges:
            if not edge.start in node_connections:
                node_connections[edge.start] = NodeConnections()
            if not edge.end in node_connections:
                node_connections[edge.end] = NodeConnections()
            node_connections[edge.start].outgoing.append(edge)
            node_connections[edge.end].incoming.append(edge)
        return node_connections

    def _filter_leaves(self,
                            nodes_in,
                            edges_in,
                            node_connections,
                            hide_single_connection_topics,
                            hide_dead_end_topics):
        '''
        removes certain ending topic nodes and their edges from list of nodes and edges

        @param hide_single_connection_topics: if true removes topics that are only published/subscribed by one node
        @param hide_dead_end_topics: if true removes topics having only publishers
        '''
        if not hide_dead_end_topics and not hide_single_connection_topics:
            return nodes_in, edges_in
        # do not manipulate incoming structures
        nodes = copy.copy(nodes_in)
        edges = copy.copy(edges_in)
        removal_nodes = []
        for n in nodes:
            if n in node_connections:
                node_edges = []
                has_out_edges = False
                node_edges.extend(node_connections[n].outgoing)
                if len(node_connections[n].outgoing) > 0:
                    has_out_edges = True
                node_edges.extend(node_connections[n].incoming)
                if ((hide_single_connection_topics and len(node_edges) < 2) or
                    (hide_dead_end_topics and not has_out_edges)):
                    removal_nodes.append(n)
                    for e in node_edges:
                        if e in edges:
                            edges.remove(e)
        for n in removal_nodes:
            nodes.remove(n)
        return nodes, edges

    def get_nodes_and_edges(self, rosgraphinst):
        """
        Get all the nodes and edges corresponding to our conductor's graph of concert clients.

        :returns: all the nodes and edges
        :rtype: (concert_client.ConcertClient[], rosgraph.impl.graph.Edge[])
        """
        nodes = rosgraphinst.concert_clients.values()
        edges = []
        for node in nodes:
            if node.msg.conn_stats.gateway_available:
                edges.append(Edge("conductor", node.concert_alias, node.link_type))
        return (nodes, edges)

    def generate_dotgraph(self,
                         rosgraphinst,
                         ns_filter,
                         topic_filter,
                         dotcode_factory,
                         show_all_advertisements=False,
                         hide_dead_end_topics=False,
                         cluster_namespaces_level=0,
                         orientation='LR',
                         rank='same',  # None, same, min, max, source, sink
                         ranksep=0.2,  # vertical distance between layers
                         rankdir='TB',  # direction of layout (TB top > bottom, LR left > right)
                         simplify=True,  # remove double edges
                         ):
        """
        See generate_dotcode
        """
        # DJS : disabling namespace/topic filtering for now
        #includes, excludes = self._split_filter_string(ns_filter)
        #connection_includes, connection_excludes = self._split_filter_string(topic_filter)

        # DJS : We don't have any use for topic nodes
        # connection_nodes = []
        # create the node definitions

        (nodes, edges) = self.get_nodes_and_edges(rosgraphinst)
        # DJS : disabling namespace/topic filtering for now
        #gateway_nodes = [n for n in gateway_nodes if matches_any(n, includes) and not matches_any(n, excludes)]
        #edges = [e for e in edges if matches_any(e.label, connection_includes) and not matches_any(e.label, connection_excludes)]

        # DJS : is this actually used?
        #unused_advertisements = not show_all_advertisements
        # DJS : connection nodes is empty?
        #edges = self._filter_orphaned_edges(edges, list(gateway_nodes) + list(connection_nodes))
        # DJS : we shouldn't have to filter orphaned edges, but just in case we might have to bring this back.
        # edges = self._filter_orphaned_edges(edges, list(nodes))
        # DJS : We don't have any use for topic nodes
        #connection_nodes = self._filter_orphaned_topics(connection_nodes, edges)
        # create the graph
        # result = "digraph G {\n  rankdir=%(orientation)s;\n%(nodes_str)s\n%(edges_str)s}\n" % vars()

        dotgraph = dotcode_factory.get_graph(rank=rank,
                                             ranksep=ranksep,
                                             simplify=simplify,
                                             rankdir=orientation)

        # DJS : We don't have any use for namespace_clusters, but might later for same ip's
#        namespace_clusters = {}

        # DJS : We don't have any use for topic nodes
#         for n in (connection_nodes or []):
#             # cluster topics with same namespace
#             if (cluster_namespaces_level > 0 and
#                 str(n).count('/') > 1 and
#                 len(str(n).split('/')[1]) > 0):
#                 namespace = str(n).split('/')[1]
#                 if namespace not in namespace_clusters:
#                     namespace_clusters[namespace] = dotcode_factory.add_subgraph_to_graph(dotgraph, namespace, rank=rank, rankdir=orientation, simplify=simplify)
#                 self._add_topic_node(n, dotcode_factory=dotcode_factory, dotgraph=namespace_clusters[namespace])
#             else:
#                 self._add_topic_node(n, dotcode_factory=dotcode_factory, dotgraph=dotgraph)

        # for ROS node, if we have created a namespace clusters for
        # one of its peer topics, drop it into that cluster
        self._add_conductor_node(dotcode_factory=dotcode_factory, dotgraph=dotgraph)
        if nodes is not None:
            for n in nodes:
                self._add_node(n, dotcode_factory=dotcode_factory, dotgraph=dotgraph)
                # DJS : We don't have any use for namespace_clusters, but might later for same ip's
#                 if (cluster_namespaces_level > 0 and
#                     str(n).count('/') >= 1 and
#                     len(str(n).split('/')[1]) > 0 and
#                     str(n).split('/')[1] in namespace_clusters):
#                     namespace = str(n).split('/')[1]
#                     self._add_node(n, rosgraphinst=rosgraphinst, dotcode_factory=dotcode_factory, dotgraph=namespace_clusters[namespace])
#                 else:
#                     self._add_node(n, rosgraphinst=rosgraphinst, dotcode_factory=dotcode_factory, dotgraph=dotgraph)
        for e in edges:
            self._add_edge(e, dotcode_factory, dotgraph=dotgraph)

        return dotgraph

    def generate_dotcode(self,
                         rosgraphinst,
                         dotcode_factory,
                         ns_filter=' ',
                         topic_filter=' ',
                         show_all_advertisements=True,
                         hide_dead_end_topics=True,
                         cluster_namespaces_level=0,
                         orientation='LR',
                         rank='same',  # None, same, min, max, source, sink
                         ranksep=0.2,  # vertical distance between layers
                         rankdir='TB',  # direction of layout (TB top > bottom, LR left > right)
                         simplify=True,  # remove double edges
                         ):
        """
        @param rosgraphinst: RosGraph instance
        @param ns_filter: nodename filter
        @type  ns_filter: string
        @param topic_filter: topicname filter
        @type  ns_filter: string
        @param orientation: rankdir value (see ORIENTATIONS dict)
        @type  dotcode_factory: object
        @param dotcode_factory: abstract factory manipulating dot language objects
        @param hide_single_connection_topics: if true remove topics with just one connection
        @param hide_dead_end_topics: if true remove topics with publishers only
        @param cluster_namespaces_level: if > 0 places box around members of same namespace (TODO: multiple namespace layers)
        @return: dotcode generated from graph singleton
        @rtype: str
        """
        dotgraph = self.generate_dotgraph(rosgraphinst=rosgraphinst,
                         ns_filter=ns_filter,
                         topic_filter=topic_filter,
                         dotcode_factory=dotcode_factory,
                         show_all_advertisements=show_all_advertisements,
                         hide_dead_end_topics=hide_dead_end_topics,
                         cluster_namespaces_level=cluster_namespaces_level,
                         orientation=orientation,
                         rank=rank,
                         ranksep=ranksep,
                         rankdir=rankdir,
                         simplify=simplify,
                         )
        dotcode = dotcode_factory.create_dot(dotgraph)
        return dotcode
