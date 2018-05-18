//
// Created by perretb on 17/05/18.
//

#pragma once

#include "../graph.hpp"
#include <stack>
#include <map>

namespace hg {

    struct region_adjacency_graph {
        ugraph rag;
        array_1d<index_t> vertex_map;
        array_1d<index_t> edge_map;
    };

    /**
     * Construct a region adjacency graph from a vertex labeled graph.
     * @tparam graph_t
     * @tparam T
     * @param graph
     * @param xvertex_labels
     * @return
     */
    template<typename graph_t, typename T>
    auto
    make_region_adjacency_graph(const graph_t &graph, const xt::xexpression<T> &xvertex_labels) {
        static_assert(std::is_integral<typename T::value_type>::value, "Labels must have an integral type.");
        auto &vertex_labels = xvertex_labels.derived_cast();
        hg_assert(vertex_labels.dimension() == 1, "Vertex labels must be scalar numbers.");
        hg_assert(vertex_labels.size() == num_vertices(graph),
                  "Vertex labels size does not match graph number of vertices.");

        using index_t = std::size_t;

        ugraph rag;

        array_1d<index_t> vertex_map({num_vertices(graph)}, invalid_index);
        array_1d<index_t> edge_map({num_edges(graph)}, invalid_index);
        
        index_t num_regions = 0;
        index_t num_edges = 0;

        std::map<std::pair<index_t, index_t>, index_t> canonical_edge;

        auto explore_component =
                [&graph, &vertex_labels, &rag, &vertex_map, &edge_map, &num_regions, &num_edges, &canonical_edge]
                        (index_t start_vertex) {
                    std::stack<index_t> s;
                    auto label_region = vertex_labels[start_vertex];

                    s.push(start_vertex);
                    vertex_map[start_vertex] = num_regions;
                    add_vertex(rag);

                    while (!s.empty()) {
                        auto v = s.top();
                        s.pop();

                        for (auto ei: out_edge_index_iterator(v, graph)) {
                            auto e = edge(ei, graph);
                            auto adjv = other_vertex(e, v, graph);
                            if (vertex_labels[adjv] == label_region) {
                                if (vertex_map[adjv] == invalid_index) {
                                    vertex_map[adjv] = num_regions;
                                    s.push(adjv);
                                }
                            } else {
                                if (vertex_map[adjv] != invalid_index) {
                                    auto num_region_adjacent = vertex_map[adjv];
                                    auto new_edge = std::make_pair(num_region_adjacent, num_regions);
                                    if (canonical_edge.count(new_edge) == 0) {
                                        add_edge(num_region_adjacent, num_regions, rag);
                                        edge_map[ei] = num_edges;
                                        canonical_edge[new_edge] = num_edges;
                                        num_edges++;
                                    } else {
                                        edge_map[ei] = canonical_edge[new_edge];
                                    }
                                }
                            }
                        }
                    }
                    num_regions++;
                };


        for (auto v: vertex_iterator(graph)) {
            if (vertex_map[v] != invalid_index)
                continue;
            explore_component(v);

        }

        return region_adjacency_graph{std::move(rag), std::move(vertex_map), std::move(edge_map)};
    }

}
