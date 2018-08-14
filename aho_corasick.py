#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/7 20:26
# @Author  : 梁浩晨
# @File    : aho_corasick.py
# @Software: PyCharm


class Node(object):

    def __init__(self, node_id, char, p_parent, p_fail=None):
        """
        仅允许root节点的char为None
        :type char: None or str
        :type p_parent: Node or None
        :type p_fail: Node or None
        """
        if isinstance(char, str) and len(char) == 0:
            raise ValueError('Node.char cannot be empty string')
        if p_parent and not isinstance(p_parent, Node):
            raise TypeError('p_parent should be None or Node')
        if p_fail and not isinstance(p_fail, Node):
            raise TypeError('p_fail should be None or Node')
        self.node_id = node_id
        self.char = char
        self.parent = p_parent
        self.fail = p_fail
        self.children = {}
        self.is_end_point = False

    def __str__(self):
        if self.char:
            ret_str = "<Node \"{}\" | node_id: {}>(node_mem_id: 0x{:x})".format(self.char, self.node_id, id(self))
        else:
            ret_str = "<Node [root] | node_id: {}>(node_mem_id: 0x{:x})".format(self.node_id, id(self))
        return ret_str

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.char == other.char

    def get_word(self):
        char_list = [self.char]
        node_now = self.parent
        while node_now.char:
            char_list.append(node_now.char)
            node_now = node_now.parent
        char_list.reverse()
        return ''.join(char_list)

    def clear(self):
        self.parent = None
        self.fail = None
        self.node_id = -1
        self.children.clear()
        self.char = None
        self.is_end_point = False


class ACTrie:
    def __init__(self, word_list):
        self.root = Node(node_id=0, char=None, p_fail=None, p_parent=None)
        self.word_set = set(word_list)
        self.node_count = 1
        self.__build()

    def __str__(self):
        return '<ACTree {}(root_mem_id:0x{:x})>'.format(self.root, id(self.root))

    def __repr__(self):
        return self.__str__()

    def clear(self):
        """
        ACTrie不再匹配任何模式串，但仍可用
        """
        self.root.clear()
        self.node_count = 1

    def __add_word(self, word: str):
        node_now = self.root
        for char in word:
            if char not in node_now.children:
                next_node = Node(self.node_count, char, p_parent=node_now)
                node_now.children[char] = next_node
                self.node_count += 1
            else:
                next_node = node_now.children.get(char)
            node_now = next_node
        node_now.is_end_point = True

    def __build(self):
        self.root.fail = None
        for word in self.word_set:
            self.__add_word(word)

        node_queue = [self.root]
        while node_queue:
            node_now = node_queue.pop(0)
            for child_char, child_node in node_now.children.items():
                fail_to = node_now.fail  # fail_to is Node
                while fail_to:
                    if child_char in fail_to.children:
                        child_node.fail = fail_to.children.get(child_char)
                        break
                    fail_to = fail_to.fail
                if not fail_to:
                    child_node.fail = self.root
                node_queue.append(child_node)

        self.root.fail = self.root

    def rebuild(self, new_word_list=None):
        self.clear()
        if new_word_list:
            self.word_set = set(new_word_list)
        self.__build()

    def search(self, sentence):
        def check_end_point(node):
            if node.is_end_point:
                word_match = node.get_word()
                if not ret.get(word_match):
                    ret[word_match] = 1
                else:
                    ret[word_match] += 1

        ret = {}
        node_now = self.root
        for char in sentence:
            if char in node_now.children:
                # 成功，单次转移
                node_now = node_now.children.get(char)
                check_end_point(node_now)
            else:
                # 失败，连续转移，直到成功或回到root
                while node_now is not self.root:
                    node_now = node_now.fail
                    check_end_point(node_now)
                    if char in node_now.children:
                        # 通过失败转移到达另一个合适的模式链
                        node_now = node_now.children.get(char)
                        check_end_point(node_now)
                        break
            # 一轮循环结束时，node_now is self.root  or  node_now.char == char

        # 收尾，回到root节点才是正常结束
        while node_now is not self.root:
            node_now = node_now.fail
            check_end_point(node_now)
        return ret


if __name__ == '__main__':
    import random
    import time

    class Timer:
        def __init__(self, name, log=True):
            self.name = name
            self.st = None
            self.ed = None
            self.log = log

        def __enter__(self):
            if self.log:
                print("{} start at {}".format(self.name, time.ctime()))
            self.st = time.time()

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.ed = time.time()
            self.time_used = self.ed - self.st
            if self.log:
                print("{} end at {}, total time use: {}".format(self.name, time.ctime(), self.ed - self.st))

    char_range = [chr(num) for num in range(ord('a'), ord('z'))] + \
                 [chr(num) for num in range(ord('A'), ord('Z'))] + \
                 [chr(num) for num in range(0x4e00, 0x9fd5)] + \
                 list('￥$&！（{》*%[^@!}(#【])）】《<>')

    # 约10w个随机模式
    pattern_list = [''.join([random.choice(char_range) for __ in range(random.randint(5, 16))]) for _ in
                    range(int(1e5))]
    pattern_list = list(set(pattern_list))

    # 长度1w字的文章
    src = ''.join([random.choice(char_range) for _ in range(int(1e4))])

    print('pattern sample:')
    print('count: {}'.format(len(pattern_list)))
    for item in pattern_list[:10]:
        print(item)

    print('\nsrc sample:')
    print(src[:100], '\n')

    with Timer('创建AC自动机'):
        ac = ACTrie(pattern_list)

    # 首次效率对比
    with Timer('AC自动机'):
        ac_ret = ac.search(src)

    with Timer('Python 原生操作符'):
        in_ret = dict([(pt, src.count(pt)) for pt in pattern_list])

    # 正确性对比
    print('========error check========')
    errors = {}

    for pt in pattern_list:
        if ac_ret.get(pt, 0) != in_ret.get(pt):
            errors[pt] = {
                'Python Count': in_ret.get(pt),
                'AC Count': ac_ret.get(pt)
            }

    if errors:
        for key, value in errors.items():
            print(key, value)
    else:
        print('all patterns return right')

    print('=========check end=========')

    # 平均耗时
    py_use = []
    ac_use = []
    ac_timer = Timer('AC自动机', log=False)
    py_timer = Timer('Python 原生操作符', log=False)
    for idx in range(100):
        with ac_timer:
            ac_ret = ac.search(src)
        ac_use.append(ac_timer.time_used)

        with py_timer:
            in_ret = dict([(pt, src.count(pt)) for pt in pattern_list])
        py_use.append(py_timer.time_used)

    print("py avg: {:5f}".format(sum(py_use) / len(py_use)))
    print('ac avg: {:5f}'.format(sum(ac_use) / len(ac_use)))

    # 重建AC自动机
    print("=======检查内存回收========")
    print('old ac id: {:x}'.format(id(ac)))
    ac_timer.log = True
    with ac_timer:
        del ac
        print(1)
    with ac_timer:
        ac = ACTrie(pattern_list)
        print(2)
    with ac_timer:
        pop_out = ac.word_set.pop()
        print('pop_out: ', pop_out)
        ac.word_set.add('123')
        ac.rebuild()
        print(3)
    # ac = ACTrie(pattern_list)
    errors = {}
    ac_ret = ac.search(src)

    for pt in pattern_list:
        if ac_ret.get(pt, 0) != in_ret.get(pt):
            errors[pt] = {
                'Python Count': in_ret.get(pt),
                'AC Count': ac_ret.get(pt)
            }

    if errors:
        for key, value in errors.items():
            print(key, value)
    else:
        print('all patterns return right')

