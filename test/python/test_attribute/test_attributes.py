############################################################################
# Copyright ESIEE Paris (2018)                                             #
#                                                                          #
# Contributor(s) : Benjamin Perret                                         #
#                                                                          #
# Distributed under the terms of the CECILL-B License.                     #
#                                                                          #
# The full license is in the file LICENSE, distributed with this software. #
############################################################################

import unittest
import numpy as np
import higra as hg


class TestAttributes(unittest.TestCase):

    @staticmethod
    def get_test_tree():
        """
        base graph is

        (0)-- 0 --(1)-- 2 --(2)
         |         |         |
         6         6         0
         |         |         |
        (3)-- 0 --(4)-- 4 --(5)
         |         |         |
         5         5         3
         |         |         |
        (6)-- 0 --(7)-- 1 --(8)

        Minima are
        A: (0,1)
        B: (3,4)
        C: (2,5)
        D: (6,7)

        BPT:




        4                 +-------16------+
                          |               |
        3         +-------15-----+        |
                  |              |        |
        2     +---14--+          |        |
              |       |          |        |
        1     |       |       +--13-+     |
              |       |       |     |     |
        0   +-9-+   +-10+   +-12+   |   +-11+
            +   +   +   +   +   +   +   +   +
            0   1   2   5   6   7   8   3   4


        :return:
        """

        g = hg.get_4_adjacency_graph((3, 3))
        edge_weights = np.asarray((0, 6, 2, 6, 0, 0, 5, 4, 5, 3, 0, 1))
        hg.CptEdgeWeightedGraph.link(edge_weights, g)

        return hg.bpt_canonical(edge_weights)

    def setUp(self):
        hg.clear_all_attributes()

    def test_area(self):
        tree, altitudes = TestAttributes.get_test_tree()

        ref_area = [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 4, 7, 9]
        area = hg.attribute_area(tree)
        self.assertTrue(np.allclose(ref_area, area))

        leaf_area = np.asarray([1, 2, 1, 1, 2, 1, 1, 1, 3])
        ref_area = [1, 2, 1, 1, 2, 1, 1, 1, 3, 3, 2, 3, 2, 5, 5, 10, 13]
        area = hg.attribute_area(tree, vertex_area=leaf_area, force_recompute=True)
        self.assertTrue(np.allclose(ref_area, area))

    def test_area_default_param(self):
        g = hg.get_4_adjacency_graph((2, 3))
        edge_weights = np.asarray((1, 4, 6, 5, 2, 7, 3))

        ref_area = (1, 1, 1, 1, 1, 1, 2, 2, 3, 3, 6)

        tree, altitudes = hg.bpt_canonical(edge_weights, g)
        area = hg.attribute_area(tree)
        self.assertTrue(np.all(ref_area == area))

        tree2 = hg.Tree(tree.parents())
        area2 = hg.attribute_area(tree2)
        self.assertTrue(np.all(ref_area == area2))

    def test_volume(self):
        tree, altitudes = TestAttributes.get_test_tree()

        ref_attribute = [0, 0, 0, 0, 0, 0, 0, 0, 1, 4, 4, 8, 2, 9, 12, 28, 36]
        attribute = hg.attribute_volume(altitudes)
        self.assertTrue(np.allclose(ref_attribute, attribute))

    def test_lca_map(self):
        tree, altitudes = TestAttributes.get_test_tree()

        ref_attribute = [9, 16, 14, 16, 10, 11, 16, 16, 16, 15, 12, 13]
        attribute = hg.attribute_lca_map(tree)
        self.assertTrue(np.allclose(ref_attribute, attribute))

    def test_frontier_length(self):
        tree, altitudes = TestAttributes.get_test_tree()

        ref_attribute = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 5]
        attribute = hg.attribute_frontier_length(tree)
        self.assertTrue(np.allclose(ref_attribute, attribute))

    def test_frontier_length_rag(self):
        g = hg.get_4_adjacency_graph((3, 3))
        vertex_labels = np.asarray(((0, 1, 1),
                                    (0, 2, 2),
                                    (3, 2, 4)))
        rag = hg.make_region_adjacency_graph_from_labelisation(vertex_labels, g)
        edge_weights = np.asarray((1, 5, 4, 3, 6, 2))
        tree, altitudes = hg.bpt_canonical(edge_weights, rag)

        ref_attribute = [0, 0, 0, 0, 0, 1, 2, 1, 4]
        attribute = hg.attribute_frontier_length(tree)
        self.assertTrue(np.allclose(ref_attribute, attribute))

    def test_frontier_strength(self):
        tree, altitudes = TestAttributes.get_test_tree()
        edge_weights = np.asarray((0, 6, 2, 6, 0, 0, 5, 4, 5, 3, 0, 1), dtype=np.float64)

        ref_attribute = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 26 / 5]

        attribute = hg.attribute_frontier_strength(tree, edge_weights)
        self.assertTrue(np.allclose(ref_attribute, attribute))

    def test_frontier_strength_rag(self):
        g = hg.get_4_adjacency_graph((3, 3))
        vertex_labels = np.asarray(((0, 1, 1),
                                    (0, 2, 2),
                                    (3, 2, 4)))
        rag = hg.make_region_adjacency_graph_from_labelisation(vertex_labels, g)
        rag_edge_weights = np.asarray((1, 5, 4, 3, 6, 2))
        tree, altitudes = hg.bpt_canonical(rag_edge_weights, rag)
        # tree is [5 5 6 7 6 7 8 8 8]
        edge_weights = np.asarray((1, 6, 2, 6, 1, 1, 5, 4, 5, 3, 1, 1), dtype=np.float64)

        ref_attribute = [0, 0, 0, 0, 0, 1, 2, 5, 9 / 4]
        attribute = hg.attribute_frontier_strength(tree, edge_weights)
        self.assertTrue(np.allclose(ref_attribute, attribute))

    def test_perimeter_length(self):
        tree, altitudes = TestAttributes.get_test_tree()
        ref_attribute = [4, 4, 4, 4, 4, 4, 4, 4, 4, 6, 6, 6, 6, 8, 10, 16, 12]
        attribute = hg.attribute_perimeter_length(tree)
        self.assertTrue(np.allclose(ref_attribute, attribute))

    def test_perimeter_length2(self):
        tree, altitudes = TestAttributes.get_test_tree()
        hg.set_attribute(hg.CptHierarchy.get_leaf_graph(tree), "no_border_vertex_out_degree", None)
        ref_attribute = [2, 3, 2, 3, 4, 3, 2, 3, 2, 3, 3, 5, 3, 3, 4, 5, 0]
        attribute = hg.attribute_perimeter_length(tree)
        self.assertTrue(np.allclose(ref_attribute, attribute))

    def test_perimeter_length_rag(self):
        g = hg.get_4_adjacency_graph((3, 3))
        vertex_labels = np.asarray(((0, 1, 1),
                                    (0, 2, 2),
                                    (3, 2, 4)))
        rag = hg.make_region_adjacency_graph_from_labelisation(vertex_labels, g)
        edge_weights = np.asarray((1, 5, 4, 3, 6, 2))
        tree, altitudes = hg.bpt_canonical(edge_weights, rag)

        ref_attribute = [3, 3, 6, 2, 2, 4, 4, 4, 0]
        attribute = hg.attribute_perimeter_length(tree)
        self.assertTrue(np.allclose(ref_attribute, attribute))

    def test_compactness(self):
        tree, altitudes = TestAttributes.get_test_tree()
        ref_attribute = [1., 1., 1., 1., 1., 1., 1., 1., 1., 0.88888889, 0.88888889, 0.88888889, 0.88888889, 0.75, 0.64,
                         0.4375, 1.]
        attribute = hg.attribute_compactness(tree)
        self.assertTrue(np.allclose(ref_attribute, attribute))

    def test_mean_weights(self):
        tree, altitudes = TestAttributes.get_test_tree()

        leaf_data = np.asarray(((0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8)),
                               dtype=np.float64)
        ref_attribute = np.asarray(((0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8),
                                    (1. / 2, 1. / 2), (7. / 2, 7. / 2), (7. / 2, 7. / 2), (13. / 2, 13. / 2), (7., 7.),
                                    (2., 2.), (29. / 7, 29. / 7), (4., 4.)))

        attribute = hg.attribute_mean_weights(tree, vertex_weights=leaf_data)
        self.assertTrue(np.allclose(ref_attribute, attribute))

    def test_sibling(self):
        t = hg.Tree((5, 5, 6, 6, 6, 7, 7, 7))
        ref = np.asarray((1, 0, 3, 4, 2, 6, 5, 7))
        res = hg.attribute_sibling(t)
        self.assertTrue(np.all(ref == res))

        t = hg.Tree((5, 5, 6, 6, 6, 7, 7, 7))
        ref2 = np.asarray((1, 0, 4, 2, 3, 6, 5, 7))
        res2 = hg.attribute_sibling(t, -1)
        self.assertTrue(np.all(ref2 == res2))

    def test_depth(self):
        t = hg.Tree((6, 6, 7, 8, 8, 8, 7, 9, 9, 9))
        ref = np.asarray((3, 3, 2, 2, 2, 2, 2, 1, 1, 0))
        res = hg.attribute_depth(t)
        self.assertTrue(np.all(ref == res))

    def test_regular_altitudes(self):
        t = hg.Tree((6, 6, 7, 8, 8, 8, 7, 9, 9, 9))
        ref = np.asarray((0, 0, 0, 0, 0, 0, 1 / 3, 2 / 3, 2 / 3, 1))
        res = hg.attribute_regular_altitudes(t)
        self.assertTrue(np.allclose(ref, res))

    def test_vertex_coordinates(self):
        g = hg.get_4_adjacency_graph((2, 3))
        ref = np.asarray((((0, 0), (0, 1), (0, 2)),
                          ((1, 0), (1, 1), (1, 2))))
        res = hg.attribute_vertex_coordinates(g)
        self.assertTrue(np.allclose(ref, res))

    def test_edge_length(self):
        g = hg.get_4_adjacency_graph((2, 3))
        ref = np.asarray((1, 1, 1, 1, 1, 1, 1))
        res = hg.attribute_edge_length(g)
        self.assertTrue(np.allclose(ref, res))

    def test_edge_length_rag(self):
        g = hg.get_4_adjacency_graph((2, 3))
        vertex_labels = np.asarray(((1, 2, 2),
                                    (3, 3, 3)))
        rag = hg.make_region_adjacency_graph_from_labelisation(vertex_labels, g)
        ref = np.asarray((1, 1, 2))
        res = hg.attribute_edge_length(rag)
        self.assertTrue(np.allclose(ref, res))

    def test_vertex_perimeter(self):
        g = hg.get_4_adjacency_graph((2, 3))
        ref = np.asarray(((4, 4, 4),
                          (4, 4, 4)))
        res = hg.attribute_vertex_perimeter(g)
        self.assertTrue(np.allclose(ref, res))

    def test_vertex_perimeter2(self):
        g = hg.get_4_adjacency_graph((2, 3))
        hg.set_attribute(g, "no_border_vertex_out_degree", None)
        ref = np.asarray(((2, 3, 2),
                          (2, 3, 2)))
        res = hg.attribute_vertex_perimeter(g)
        self.assertTrue(np.allclose(ref, res))

    def test_vertex_perimeter_rag(self):
        g = hg.get_4_adjacency_graph((2, 3))
        vertex_labels = np.asarray(((1, 2, 2),
                                    (3, 3, 3)))
        rag = hg.make_region_adjacency_graph_from_labelisation(vertex_labels, g)
        ref = np.asarray((2, 3, 3))
        res = hg.attribute_vertex_perimeter(rag)
        self.assertTrue(np.allclose(ref, res))

    def test_attribute_vertex_list(self):
        tree, altitudes = TestAttributes.get_test_tree()

        res = hg.attribute_vertex_list(tree)
        ref = [[0], [1], [2], [3], [4], [5], [6], [7], [8],
               [0, 1], [2, 5], [3, 4], [6, 7], [6, 7, 8],
               [0, 1, 2, 5], [0, 1, 2, 5, 6, 7, 8],
               [0, 1, 2, 5, 6, 7, 8, 3, 4]]
        self.assertTrue(len(ref) == len(res))
        for i in range(len(ref)):
            self.assertTrue(set(ref[i]) == set(res[i]))

    def test_attribute_gaussian_region_weights_model_scalar(self):
        tree, altitudes = TestAttributes.get_test_tree()
        vertex_list = hg.attribute_vertex_list(tree)

        np.random.seed(42)
        vertex_weights = np.random.rand(tree.num_leaves())
        mean, variance = hg.attribute_gaussian_region_weights_model(tree, vertex_weights)

        for i in tree.leaves_to_root_iterator():
            m = np.mean(vertex_weights[vertex_list[i]])
            v = np.var(vertex_weights[vertex_list[i]])
            self.assertTrue(np.isclose(m, mean[i]))
            self.assertTrue(np.isclose(v, variance[i]))

    def test_attribute_gaussian_region_weights_model_vectorial(self):
        tree, altitudes = TestAttributes.get_test_tree()
        vertex_list = hg.attribute_vertex_list(tree)

        np.random.seed(42)
        vertex_weights = np.random.rand(tree.num_leaves(), 3)
        mean, variance = hg.attribute_gaussian_region_weights_model(tree, vertex_weights)

        for i in tree.leaves_to_root_iterator(include_leaves=True):
            m = np.mean(vertex_weights[vertex_list[i]], 0)

            self.assertTrue(np.allclose(m, mean[i, :]))

            # numpy wrongly interprets a single observation with several variables as
            # multiple observations of a single variables
            if i >= tree.num_leaves():
                v = np.cov(vertex_weights[vertex_list[i]], rowvar=False, bias=True)
                self.assertTrue(np.allclose(v, variance[i, ...]))
            else:
                v = np.zeros_like(variance[i, ...])
                self.assertTrue(np.allclose(v, variance[i, ...]))


if __name__ == '__main__':
    unittest.main()
