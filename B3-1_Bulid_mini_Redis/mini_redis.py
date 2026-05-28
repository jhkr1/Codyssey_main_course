import shlex
import time

from doubly_linked_list import DoublyLinkedList
from hash_map import HashMap
from min_heap import MinHeap


class RedisEntry:
    """The string value stored for one key."""

    def __init__(self, value):
        self.value = value


class MiniRedis:
    """A small Redis-like engine backed by handmade data structures."""

    def __init__(self):
        self.store = HashMap()
        self.lru = DoublyLinkedList()
        self.lru_nodes = HashMap()
        self.expires = HashMap()
        self.expire_heap = MinHeap()
        self.used_memory = 0
        self.maxmemory = 0
        self.evicted_keys = 0

    def execute(self, line):
        try:
            parts = shlex.split(line)
        except ValueError as error:
            return "(error) ERR " + str(error)

        if len(parts) == 0:
            return ""

        command = parts[0].upper()
        args = parts[1:]

        if command == "SET":
            return self._cmd_set(command, args)
        if command == "GET":
            return self._cmd_get(command, args)
        if command == "DEL":
            return self._cmd_del(command, args)
        if command == "EXISTS":
            return self._cmd_exists(command, args)
        if command == "DBSIZE":
            return self._cmd_dbsize(command, args)
        if command == "KEYS":
            return self._cmd_keys(command, args)
        if command == "CONFIG":
            return self._cmd_config(command, args)
        if command == "INFO":
            return self._cmd_info(command, args)
        if command == "EXPIRE":
            return self._cmd_expire(command, args)
        if command == "TTL":
            return self._cmd_ttl(command, args)
        return "(error) ERR unknown command '" + command + "'"

    def _cmd_set(self, command, args):
        if len(args) != 2:
            return self._wrong_args(command)

        key = args[0]
        value = args[1]
        self._delete_if_expired(key)

        entry_memory = self._entry_memory(key, value)
        if self.maxmemory > 0 and entry_memory > self.maxmemory:
            return "(error) OOM command not allowed when used_memory > 'maxmemory'"

        old_entry = self.store.get(key)
        if old_entry is None:
            self.used_memory += entry_memory
            self.store.put(key, RedisEntry(value))
            self._add_lru_key(key)
        else:
            self.used_memory -= self._entry_memory(key, old_entry.value)
            self.used_memory += entry_memory
            old_entry.value = value
            self._touch_lru_key(key)

        self.expires.remove(key)
        self._evict_until_memory_fits()
        return "OK"

    def _cmd_get(self, command, args):
        if len(args) != 1:
            return self._wrong_args(command)

        key = args[0]
        if self._delete_if_expired(key):
            return "(nil)"

        entry = self.store.get(key)
        if entry is None:
            return "(nil)"

        self._touch_lru_key(key)
        return '"' + entry.value + '"'

    def _cmd_del(self, command, args):
        if len(args) != 1:
            return self._wrong_args(command)

        if self._delete_if_expired(args[0]):
            return "(integer) 0"

        removed = self._delete_key(args[0], count_eviction=False)
        if removed:
            return "(integer) 1"
        return "(integer) 0"

    def _cmd_exists(self, command, args):
        if len(args) != 1:
            return self._wrong_args(command)

        key = args[0]
        self._delete_if_expired(key)
        if self.store.contains(key):
            return "(integer) 1"
        return "(integer) 0"

    def _cmd_dbsize(self, command, args):
        if len(args) != 0:
            return self._wrong_args(command)
        self._purge_expired_keys()
        return "(integer) " + str(self.store.size())

    def _cmd_keys(self, command, args):
        if len(args) != 0:
            return self._wrong_args(command)
        self._purge_expired_keys()
        keys = self.store.keys()
        if len(keys) == 0:
            return "(empty array)"

        lines = []
        for key in keys:
            lines.append('"' + key + '"')
        return "\n".join(lines)

    def _cmd_config(self, command, args):
        if len(args) != 3 or args[0].upper() != "SET" or args[1].lower() != "maxmemory":
            return self._wrong_args(command)

        maxmemory = self._parse_non_negative_int(args[2])
        if maxmemory is None:
            return "(error) ERR value is not an integer or out of range"

        self.maxmemory = maxmemory
        self._evict_until_memory_fits()
        return "OK"

    def _cmd_info(self, command, args):
        if len(args) != 1 or args[0].lower() != "memory":
            return self._wrong_args(command)
        self._purge_expired_keys()
        return (
            "used_memory:" + str(self.used_memory) + "\n"
            + "maxmemory:" + str(self.maxmemory) + "\n"
            + "evicted_keys:" + str(self.evicted_keys)
        )

    def _cmd_expire(self, command, args):
        if len(args) != 2:
            return self._wrong_args(command)

        key = args[0]
        seconds = self._parse_int(args[1])
        if seconds is None:
            return "(error) ERR value is not an integer or out of range"

        self._delete_if_expired(key)
        if not self.store.contains(key):
            return "(integer) 0"

        if seconds <= 0:
            self._delete_key(key, count_eviction=False)
            return "(integer) 1"

        expire_at = time.time() + seconds
        self.expires.put(key, expire_at)
        self.expire_heap.push((expire_at, key))
        return "(integer) 1"

    def _cmd_ttl(self, command, args):
        if len(args) != 1:
            return self._wrong_args(command)

        key = args[0]
        self._delete_if_expired(key)
        if not self.store.contains(key):
            return "(integer) -2"

        expire_at = self.expires.get(key)
        if expire_at is None:
            return "(integer) -1"

        remaining = int(expire_at - time.time())
        if remaining < 0:
            remaining = 0
        return "(integer) " + str(remaining)

    def _entry_memory(self, key, value):
        return len(key.encode("utf-8")) + len(value.encode("utf-8"))

    def _add_lru_key(self, key):
        node = self.lru.insert_front(key)
        self.lru_nodes.put(key, node)

    def _touch_lru_key(self, key):
        node = self.lru_nodes.get(key)
        if node is None:
            self._add_lru_key(key)
            return
        new_node = self.lru.move_to_front(node)
        self.lru_nodes.put(key, new_node)

    def _remove_lru_key(self, key):
        node = self.lru_nodes.remove(key)
        if node is not None:
            self.lru.remove_node(node)

    def _delete_key(self, key, count_eviction):
        entry = self.store.remove(key)
        if entry is None:
            return False

        self.used_memory -= self._entry_memory(key, entry.value)
        self.expires.remove(key)
        self._remove_lru_key(key)
        if count_eviction:
            self.evicted_keys += 1
        return True

    def _delete_if_expired(self, key):
        expire_at = self.expires.get(key)
        if expire_at is None:
            return False
        if expire_at <= time.time():
            self._delete_key(key, count_eviction=False)
            return True
        return False

    def _purge_expired_keys(self):
        now = time.time()
        while self.expire_heap.size() > 0:
            item = self.expire_heap.peek()
            expire_at = item[0]
            key = item[1]
            if expire_at > now:
                break

            self.expire_heap.pop()
            current_expire_at = self.expires.get(key)
            if current_expire_at is not None and current_expire_at == expire_at:
                self._delete_key(key, count_eviction=False)

    def _evict_until_memory_fits(self):
        if self.maxmemory == 0:
            return

        while self.used_memory > self.maxmemory:
            least_recent_key = self.lru.tail.data if self.lru.tail is not None else None
            if least_recent_key is None:
                break
            self._delete_key(least_recent_key, count_eviction=True)

    def _parse_int(self, text):
        try:
            return int(text)
        except ValueError:
            return None

    def _parse_non_negative_int(self, text):
        value = self._parse_int(text)
        if value is None or value < 0:
            return None
        return value

    def _wrong_args(self, command):
        return "(error) ERR wrong number of arguments for '" + command + "' command"
