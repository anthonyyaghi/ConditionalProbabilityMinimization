class Node(object):
    def __init__(self, data, element, good):
        self.data = data
        self.element = element
        self.good = good
        self.children = []

    def add_child(self, obj):
        self.children.append(obj)
