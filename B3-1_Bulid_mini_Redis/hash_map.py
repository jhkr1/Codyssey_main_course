from doubly_linked_list import DoublyLinkedList


class HashEntry:
    """A key-value pair stored inside one hash bucket chain."""

    def __init__(self, key, value):
        self.key = key
        self.value = value


class HashMap:
    """Hash map implemented with separate chaining.

    Buckets are arrays, and each bucket is a doubly linked list. The map grows
    when the load factor becomes greater than 0.75.
    """

    def __init__(self, capacity=8):
        self.capacity = capacity
        self.count = 0
        self.buckets = self._make_buckets(capacity)

    def _make_buckets(self, capacity):
        buckets = []
        for _ in range(capacity):
            buckets.append(DoublyLinkedList())
        return buckets

    def _hash(self, key):
        text = str(key)
        hash_value = 5381
        for char in text:
            hash_value = ((hash_value * 33) + ord(char)) % 2147483647
        return hash_value

    def _bucket_index(self, key):
        return self._hash(key) % self.capacity

    def _find_node(self, key):
        bucket = self.buckets[self._bucket_index(key)]
        current = bucket.head
        while current is not None:
            if current.data.key == key:
                return current
            current = current.next
        return None

    def put(self, key, value):
        node = self._find_node(key)
        if node is not None:
            node.data.value = value
            return

        index = self._bucket_index(key)
        self.buckets[index].insert_back(HashEntry(key, value))
        self.count += 1

        if self.count / self.capacity > 0.75:
            self._resize()

    def get(self, key):
        node = self._find_node(key)
        if node is None:
            return None
        return node.data.value

    def remove(self, key):
        index = self._bucket_index(key)
        bucket = self.buckets[index]
        current = bucket.head
        while current is not None:
            if current.data.key == key:
                value = current.data.value
                bucket.remove_node(current)
                self.count -= 1
                return value
            current = current.next
        return None

    def contains(self, key):
        return self._find_node(key) is not None

    def keys(self):
        result = []
        for bucket in self.buckets:
            current = bucket.head
            while current is not None:
                result.append(current.data.key)
                current = current.next
        return result

    def size(self):
        return self.count

    def _resize(self):
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = self._make_buckets(self.capacity)
        old_count = self.count
        self.count = 0

        for bucket in old_buckets:
            current = bucket.head
            while current is not None:
                self.put(current.data.key, current.data.value)
                current = current.next
        self.count = old_count
