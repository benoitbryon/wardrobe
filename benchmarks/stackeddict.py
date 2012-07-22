#!/usr/bin/env python
# coding=utf-8
"""Benchmarks for wardrobe module."""
import benchmark

from wardrobe import StackedDict


class BenchmarkStackedDict(benchmark.Benchmark):
    """Benchmarks for :py:class:`wardrobe.stackeddict.StackedDict`."""
    def setUp(self):
        """Prepare data outside benchmarks."""
        layer_size = 100
        layer_count = 100
        self.layers = []
        for layer_num in range(0, layer_count + 1):
            layer_start = layer_num * int(layer_size / 2)
            layer_end = layer_start + layer_size
            layer = dict.fromkeys(range(layer_start , layer_end),
                                  'Hello world!')
            self.layers.append(layer)
        self.key_range = range(0, layer_end)
        self.stackeddict = self._setitem()
        self.dict = self._dict_setitem()

    def _setitem(self):
        s = StackedDict()
        for layer in self.layers:
            for key, value in layer.items():
                s[key] = value
        return s

    def _dict_setitem(self):
        d = dict()
        for layer in self.layers:
            for key, value in layer.items():
                d[key] = value
        return d

    def test_setitem(self):
        """Benchmark :py:meth:`StackedDict.__setitem__`."""
        self._setitem()
        
    def test_dict_setitem(self):
        """Benchmark standard dict's __setitem__ for comparison purpose."""
        self._dict_setitem()

    def test_getitem(self):
        """Benckmark :py:meth:`StackedDict.__getitem__`."""
        for key in self.key_range:
            self.stackeddict[key]

    def test_dict_getitem(self):
        """Benckmark standard dict's __getitem__ for comparison purpose."""
        for key in self.key_range:
            self.dict[key]

    def test_iter(self):
        """Benchmark :py:meth:`StackedDict.__iter__`."""
        for break_threshold in range(0, 10):
            for key in iter(self.stackeddict):
                if key > break_threshold:
                    break

    def test_dict_iter(self):
        """Benchmark standard dict's __iter__ for comparison purpose."""
        for break_threshold in range(0, 10):
            for key in iter(self.dict):
                if key > break_threshold:
                    break


if __name__ == '__main__':
    benchmark.main(format="markdown", numberFormat="%.4g", each=100,
                   sort_by='name')
