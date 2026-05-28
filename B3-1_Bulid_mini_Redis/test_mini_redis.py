import time
import unittest

from hash_map import HashMap
from mini_redis import MiniRedis
from min_heap import MinHeap


class MiniRedisTest(unittest.TestCase):
    def test_string_commands(self):
        redis = MiniRedis()

        self.assertEqual(redis.execute('SET user:1 "Alice"'), "OK")
        self.assertEqual(redis.execute("GET user:1"), '"Alice"')
        self.assertEqual(redis.execute("EXISTS user:1"), "(integer) 1")
        self.assertEqual(redis.execute("DBSIZE"), "(integer) 1")
        self.assertEqual(redis.execute("DEL user:1"), "(integer) 1")
        self.assertEqual(redis.execute("GET user:1"), "(nil)")

    def test_lru_eviction(self):
        redis = MiniRedis()

        self.assertEqual(redis.execute("CONFIG SET maxmemory 30"), "OK")
        self.assertEqual(redis.execute('SET user:1 "Alice"'), "OK")
        self.assertEqual(redis.execute('SET user:2 "Bob"'), "OK")
        self.assertEqual(redis.execute('SET user:3 "Charlie"'), "OK")

        self.assertEqual(redis.execute("GET user:1"), "(nil)")
        self.assertIn("evicted_keys:1", redis.execute("INFO memory"))

    def test_ttl(self):
        redis = MiniRedis()

        self.assertEqual(redis.execute("SET a b"), "OK")
        self.assertEqual(redis.execute("EXPIRE a 1"), "(integer) 1")
        self.assertIn(redis.execute("TTL a"), ["(integer) 0", "(integer) 1"])
        time.sleep(1.1)
        self.assertEqual(redis.execute("GET a"), "(nil)")
        self.assertEqual(redis.execute("TTL a"), "(integer) -2")

    def test_del_treats_expired_key_as_missing(self):
        redis = MiniRedis()

        self.assertEqual(redis.execute("SET a b"), "OK")
        self.assertEqual(redis.execute("EXPIRE a 1"), "(integer) 1")
        time.sleep(1.1)
        self.assertEqual(redis.execute("DEL a"), "(integer) 0")

    def test_set_clears_ttl(self):
        redis = MiniRedis()

        self.assertEqual(redis.execute("SET a b"), "OK")
        self.assertEqual(redis.execute("EXPIRE a 10"), "(integer) 1")
        self.assertEqual(redis.execute("SET a c"), "OK")
        self.assertEqual(redis.execute("TTL a"), "(integer) -1")

    def test_oom_single_entry(self):
        redis = MiniRedis()

        self.assertEqual(redis.execute("CONFIG SET maxmemory 3"), "OK")
        self.assertEqual(
            redis.execute("SET long value"),
            "(error) OOM command not allowed when used_memory > 'maxmemory'",
        )
        self.assertEqual(redis.execute("DBSIZE"), "(integer) 0")


class DataStructureTest(unittest.TestCase):
    def test_hash_map_resizes_and_keeps_values(self):
        table = HashMap(capacity=2)
        for index in range(10):
            table.put("k" + str(index), "v" + str(index))

        self.assertEqual(table.size(), 10)
        self.assertEqual(table.get("k7"), "v7")
        self.assertTrue(table.capacity >= 16)

    def test_min_heap_orders_by_expire_time(self):
        heap = MinHeap()
        heap.push((3, "c"))
        heap.push((1, "a"))
        heap.push((2, "b"))

        self.assertEqual(heap.pop(), (1, "a"))
        self.assertEqual(heap.pop(), (2, "b"))
        self.assertEqual(heap.pop(), (3, "c"))


if __name__ == "__main__":
    unittest.main()
