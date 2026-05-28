class MinHeap:
    """A minimum heap for values comparable with the < operator."""

    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)
        self._heapify_up(len(self.items) - 1)

    def pop(self):
        if len(self.items) == 0:
            return None
        if len(self.items) == 1:
            return self.items.pop()

        root = self.items[0]
        self.items[0] = self.items.pop()
        self._heapify_down(0)
        return root

    def peek(self):
        if len(self.items) == 0:
            return None
        return self.items[0]

    def size(self):
        return len(self.items)

    def _heapify_up(self, index):
        while index > 0:
            parent = (index - 1) // 2
            if self.items[parent] <= self.items[index]:
                break
            self.items[parent], self.items[index] = self.items[index], self.items[parent]
            index = parent

    def _heapify_down(self, index):
        length = len(self.items)
        while True:
            left = index * 2 + 1
            right = index * 2 + 2
            smallest = index

            if left < length and self.items[left] < self.items[smallest]:
                smallest = left
            if right < length and self.items[right] < self.items[smallest]:
                smallest = right
            if smallest == index:
                break

            self.items[index], self.items[smallest] = self.items[smallest], self.items[index]
            index = smallest
