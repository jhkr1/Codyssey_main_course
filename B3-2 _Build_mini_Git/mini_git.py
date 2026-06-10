"""Mini Git의 핵심 자료구조와 알고리즘.

main.py는 실행 진입점만 담당하고, 이 파일은 커밋 그래프, 브랜치,
검색 인덱스, 탐색/정렬 알고리즘을 담당합니다.
"""

from collections import deque
from dataclasses import dataclass
from datetime import datetime
import shlex


@dataclass
class Commit:
    """커밋 그래프의 노드 하나."""

    hash: str
    message: str
    author: str
    timestamp: datetime
    parents: list[str]


def normalize_token(text: str) -> str:
    """검색 인덱스에서 대소문자 차이를 없애기 위해 토큰을 정규화한다."""
    return text.lower()


def merge_sort(items, compare):
    """Python 정렬 API 없이 직접 구현한 안정 merge sort.

    compare(a, b)는 a가 먼저 오면 음수, 같으면 0, b가 먼저 오면 양수를
    반환해야 합니다. 같은 값일 때 왼쪽 원소를 먼저 넣기 때문에 안정 정렬입니다.
    """
    length = len(items)
    if length <= 1:
        return items[:]

    mid = length // 2
    left = merge_sort(items[:mid], compare)
    right = merge_sort(items[mid:], compare)
    return merge(left, right, compare)


def merge(left, right, compare):
    """이미 정렬된 두 리스트를 하나의 정렬된 리스트로 합친다."""
    result = []
    left_i = 0
    right_i = 0

    while left_i < len(left) and right_i < len(right):
        if compare(left[left_i], right[right_i]) <= 0:
            result.append(left[left_i])
            left_i += 1
        else:
            result.append(right[right_i])
            right_i += 1

    while left_i < len(left):
        result.append(left[left_i])
        left_i += 1

    while right_i < len(right):
        result.append(right[right_i])
        right_i += 1

    return result


def compare_strings(a: str, b: str) -> int:
    """문자열을 사전순으로 비교한다."""
    if a < b:
        return -1
    if a > b:
        return 1
    return 0


def compare_paths(a: list[str], b: list[str]) -> int:
    """경로를 'h1->h2->...' 문자열로 바꿔 사전순 비교한다."""
    return compare_strings("->".join(a), "->".join(b))


class InvertedIndex:
    """커밋 검색을 빠르게 하기 위한 역색인."""

    def __init__(self):
        self.keyword_to_hashes = {}
        self.author_to_hashes = {}

    def add_commit(self, commit: Commit):
        """커밋 하나를 keyword 인덱스와 author 인덱스에 추가한다."""
        author_key = normalize_token(commit.author)
        self._append_unique(self.author_to_hashes, author_key, commit.hash)

        seen_tokens = set()
        for raw_token in commit.message.split():
            token = normalize_token(raw_token)
            if token and token not in seen_tokens:
                self._append_unique(self.keyword_to_hashes, token, commit.hash)
                seen_tokens.add(token)

    def search_keyword(self, keyword: str) -> list[str]:
        """메시지에 키워드가 들어간 커밋 해시 목록을 반환한다.

        'login feature'처럼 여러 단어가 들어오면 모든 단어를 포함하는 커밋만
        후보로 남깁니다. 후보는 역색인에서 가져오므로 전체 커밋 순회보다 빠릅니다.
        """
        tokens = []
        seen_tokens = set()
        for raw_token in keyword.split():
            token = normalize_token(raw_token)
            if token and token not in seen_tokens:
                tokens.append(token)
                seen_tokens.add(token)

        if len(tokens) == 0:
            return []

        candidates = self.keyword_to_hashes.get(tokens[0], [])[:]
        for token in tokens[1:]:
            token_hashes = set(self.keyword_to_hashes.get(token, []))
            filtered = []
            for commit_hash in candidates:
                if commit_hash in token_hashes:
                    filtered.append(commit_hash)
            candidates = filtered

        return candidates

    def search_author(self, author: str) -> list[str]:
        """작성자 이름으로 커밋 해시 목록을 반환한다."""
        return self.author_to_hashes.get(normalize_token(author), [])[:]

    def _append_unique(self, table, key, commit_hash):
        if key not in table:
            table[key] = []
        if commit_hash not in table[key]:
            table[key].append(commit_hash)


class MiniGitRepository:
    """메모리에서 동작하는 Mini Git 저장소."""

    def __init__(self):
        self.initialized = False
        self.current_user = None
        self.current_branch = None
        self.branches = {}
        self.commits = {}
        self.hash_counter = 0
        self.index = InvertedIndex()

    def init(self, user_name: str) -> str:
        """저장소를 초기화하고 main 브랜치를 만든다."""
        self.initialized = True
        self.current_user = user_name
        self.current_branch = "main"
        self.branches = {"main": None}
        self.commits = {}
        self.hash_counter = 0
        self.index = InvertedIndex()
        return (
            "Initialized repository.\n"
            "Current branch: main\n"
            f"Current user: {user_name}"
        )

    def create_branch(self, branch_name: str) -> str:
        """현재 HEAD 커밋을 가리키는 새 브랜치를 만든다."""
        self._require_initialized()
        if branch_name in self.branches:
            return f"Branch already exists: {branch_name}"
        self.branches[branch_name] = self._head_hash()
        return f"Created branch: {branch_name}"

    def switch(self, branch_name: str) -> str:
        """현재 브랜치를 변경한다."""
        self._require_initialized()
        if branch_name not in self.branches:
            return f"Unknown branch: {branch_name}"
        self.current_branch = branch_name
        return f"Switched to branch: {branch_name}"

    def commit(self, message: str) -> str:
        """현재 HEAD를 부모로 하는 새 커밋을 만든다."""
        self._require_initialized()
        parent = self._head_hash()
        parents = [] if parent is None else [parent]
        commit_hash = self._next_hash()
        commit = Commit(
            hash=commit_hash,
            message=message,
            author=self.current_user,
            timestamp=datetime.now(),
            parents=parents,
        )
        self.commits[commit_hash] = commit
        self.branches[self.current_branch] = commit_hash
        self.index.add_commit(commit)
        return f"[{self.current_branch} {commit_hash}] {message}"

    def log(self, sort_by=None) -> str:
        """커밋 로그를 부모 우선 또는 지정된 기준으로 출력한다."""
        self._require_initialized()
        commits = self._all_commits_parent_first()

        if sort_by == "date":
            commits = merge_sort(commits, self._compare_by_date)
        elif sort_by == "author":
            commits = merge_sort(commits, self._compare_by_author)
        elif sort_by is not None:
            return "Invalid args"

        if len(commits) == 0:
            return "No commits."
        return self._format_commit_list(commits)

    def ancestors(self, commit_hash: str) -> str:
        """부모 방향 DFS로 모든 조상 커밋을 찾는다."""
        self._require_initialized()
        if commit_hash not in self.commits:
            return f"Unknown commit: {commit_hash}"

        result = []
        visited = set()
        stack = self.commits[commit_hash].parents[:]

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            result.append(current)
            for parent in self.commits[current].parents:
                if parent not in visited:
                    stack.append(parent)

        if len(result) == 0:
            return "No ancestors."
        hashes = merge_sort(result, compare_strings)
        return "Ancestors: " + " -> ".join(hashes)

    def path(self, start_hash: str, end_hash: str) -> str:
        """부모 연결을 무방향 간선으로 보고 BFS 최단 경로를 찾는다."""
        self._require_initialized()
        if start_hash not in self.commits:
            return f"Unknown commit: {start_hash}"
        if end_hash not in self.commits:
            return f"Unknown commit: {end_hash}"

        if start_hash == end_hash:
            return f"Path: {start_hash}"

        adjacency = self._undirected_adjacency()
        queue = deque([[start_hash]])
        best_depth_by_hash = {start_hash: 0}
        found_paths = []
        found_depth = None

        while queue:
            path = queue.popleft()
            current = path[-1]
            depth = len(path) - 1

            if found_depth is not None and depth >= found_depth:
                continue

            neighbors = merge_sort(adjacency.get(current, []), compare_strings)
            for neighbor in neighbors:
                if neighbor in path:
                    continue

                next_path = path + [neighbor]
                next_depth = depth + 1

                if found_depth is not None and next_depth > found_depth:
                    continue

                if neighbor == end_hash:
                    found_depth = next_depth
                    found_paths.append(next_path)
                    continue

                known_depth = best_depth_by_hash.get(neighbor)
                if known_depth is None or next_depth <= known_depth:
                    best_depth_by_hash[neighbor] = next_depth
                    queue.append(next_path)

        if len(found_paths) == 0:
            return "No path"

        best = found_paths[0]
        for candidate in found_paths[1:]:
            if compare_paths(candidate, best) < 0:
                best = candidate
        return "Path: " + " -> ".join(best)

    def search_keyword(self, keyword: str) -> str:
        """키워드 역색인으로 커밋을 검색한다."""
        self._require_initialized()
        hashes = self.index.search_keyword(keyword)
        return self._format_search_result(hashes)

    def search_author(self, author: str) -> str:
        """작성자 역색인으로 커밋을 검색한다."""
        self._require_initialized()
        hashes = self.index.search_author(author)
        return self._format_search_result(hashes)

    def _all_commits_parent_first(self) -> list[Commit]:
        visited = set()
        result = []

        for commit_hash in self.commits:
            self._visit_parent_first(commit_hash, visited, result)

        return result

    def _visit_parent_first(self, commit_hash: str, visited: set, result: list[Commit]):
        if commit_hash in visited:
            return

        commit = self.commits[commit_hash]
        for parent_hash in commit.parents:
            self._visit_parent_first(parent_hash, visited, result)

        visited.add(commit_hash)
        result.append(commit)

    def _undirected_adjacency(self):
        adjacency = {}
        for commit_hash in self.commits:
            adjacency[commit_hash] = []

        for commit in self.commits.values():
            for parent in commit.parents:
                adjacency[commit.hash].append(parent)
                adjacency[parent].append(commit.hash)

        return adjacency

    def _next_hash(self) -> str:
        self.hash_counter += 1
        commit_hash = f"c{self.hash_counter:06d}"
        while commit_hash in self.commits:
            self.hash_counter += 1
            commit_hash = f"c{self.hash_counter:06d}"
        return commit_hash

    def _head_hash(self):
        return self.branches[self.current_branch]

    def _require_initialized(self):
        if not self.initialized:
            raise RuntimeError("Repository not initialized.")

    def _compare_by_date(self, a: Commit, b: Commit) -> int:
        if a.timestamp < b.timestamp:
            return -1
        if a.timestamp > b.timestamp:
            return 1
        return compare_strings(a.hash, b.hash)

    def _compare_by_author(self, a: Commit, b: Commit) -> int:
        author_cmp = compare_strings(a.author.lower(), b.author.lower())
        if author_cmp != 0:
            return author_cmp
        return self._compare_by_date(a, b)

    def _format_commit_list(self, commits: list[Commit]) -> str:
        lines = []
        for commit in commits:
            branch_names = self._branches_pointing_to(commit.hash)
            branch_text = "" if len(branch_names) == 0 else " [" + ", ".join(branch_names) + "]"
            timestamp = commit.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"commit {commit.hash} ({commit.author}, {timestamp}){branch_text}")
            lines.append(commit.message)
        return "\n".join(lines)

    def _format_search_result(self, hashes: list[str]) -> str:
        if len(hashes) == 0:
            return "Found 0 commits."

        commits = []
        for commit_hash in hashes:
            commits.append(self.commits[commit_hash])

        commits = merge_sort(commits, self._compare_by_date)
        lines = [f"Found {len(commits)} commit:" if len(commits) == 1 else f"Found {len(commits)} commits:"]
        for commit in commits:
            lines.append(f"- {commit.hash}: {commit.message}")
        return "\n".join(lines)

    def _branches_pointing_to(self, commit_hash: str) -> list[str]:
        names = []
        for branch_name, branch_hash in self.branches.items():
            if branch_hash == commit_hash:
                names.append(branch_name)
        return merge_sort(names, compare_strings)


class MiniGitCLI:
    """명령어 파싱과 REPL 실행을 담당한다."""

    def __init__(self):
        self.repo = MiniGitRepository()

    def execute(self, line: str) -> str | None:
        """사용자 입력 한 줄을 파싱하고 명령을 실행한다."""
        try:
            parts = shlex.split(line)
        except ValueError:
            return "Invalid args"

        if len(parts) == 0:
            return ""

        command = parts[0].lower()
        args = parts[1:]

        if command in ("exit", "quit"):
            return None

        try:
            if command == "init":
                if len(args) != 1:
                    return "Invalid args"
                return self.repo.init(args[0])

            if command == "branch":
                if len(args) != 1:
                    return "Invalid args"
                return self.repo.create_branch(args[0])

            if command == "switch":
                if len(args) != 1:
                    return "Invalid args"
                return self.repo.switch(args[0])

            if command == "commit":
                if len(args) != 1:
                    return "Invalid args"
                return self.repo.commit(args[0])

            if command == "log":
                if len(args) == 0:
                    return self.repo.log()
                if len(args) == 1 and args[0].startswith("--sort-by="):
                    return self.repo.log(args[0][len("--sort-by="):])
                return "Invalid args"

            if command == "path":
                if len(args) != 2:
                    return "Invalid args"
                return self.repo.path(args[0], args[1])

            if command == "ancestors":
                if len(args) != 1:
                    return "Invalid args"
                return self.repo.ancestors(args[0])

            if command == "search":
                if len(args) != 1:
                    return "Invalid args"
                if args[0].startswith("--author="):
                    author = args[0][len("--author="):]
                    if author == "":
                        return "Invalid args"
                    return self.repo.search_author(author)
                return self.repo.search_keyword(args[0])

            return f"Unknown command: {parts[0]}"
        except RuntimeError as error:
            return str(error)

    def run(self):
        """mini-git 프롬프트를 반복 실행한다."""
        while True:
            try:
                line = input("mini-git> ")
            except EOFError:
                print()
                break

            result = self.execute(line)
            if result is None:
                break
            if result:
                print(result)
