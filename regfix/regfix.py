from collections import deque
from random import choice
from typing import List, Dict, Tuple, Deque, Optional
from .regex import RegEx, Leaf

class SearchState :
    def __init__(self, state:Leaf, pos:int) :
        self.state = state
        self.pos = pos
    
    def __hash__(self) :
        return hash((self.state, self.pos))
    
    def __eq__(self, another) :
        return (self.state, self.pos) == (another.state, another.pos)

    def __ne__(self, another) :
        return not self == another

class SearchEdge :
    def __init__(self, action:str, prev:SearchState) :
        self.action = action
        self.prev = prev

class SearchNode :
    def __init__(self, cost: int, edges: List[SearchEdge]) :
        self.cost = cost
        self.edges = edges

class RegFix:
    def __init__(self, regex:RegEx, errstr:str, max_cost:int=4) :
        dist:Dict[Leaf, SearchNode] = dict()

        # 0/1 BFS: using deque
        deq:Deque[Tuple[SearchState, SearchEdge, bool]] = deque()

        for init_state in regex.term.first :
            search_state = SearchState(init_state, 0)
            deq.append((search_state, None, False))
            dist[search_state] = SearchNode(0, [])

        termini = None
        total_cost:int = 2**63 - 1
        
        def update_state(s:SearchState, action:str, last:SearchState, one:bool) :
            nonlocal total_cost, max_cost
            term = (s, SearchEdge(action, last), one)
            cost = dist[last].cost + int(one)
            if cost > max_cost :
                return
            if cost > total_cost : 
                return
            if s in dist and dist[s].cost < cost :
                return
            if one :
                deq.append(term)
            else :
                deq.appendleft(term)

        def dfs_gen() :
            nonlocal total_cost, termini
            while deq :
                s, edge, one = deq.popleft()
                if edge is None :
                    yield s
                    continue
                action, last = edge.action, edge.prev
                cost = dist[last].cost + int(one)
                if cost > total_cost : 
                    continue
                if s in dist :
                    if dist[s].cost == cost :
                        dist[s].edges.append(SearchEdge(action, last))
                else :
                    dist[s] = SearchNode(cost, [SearchEdge(action, last)])
                    if s.pos == len(errstr) and s.state.is_terminator :
                        total_cost = cost
                        termini = s.state
                yield s

        for st in dfs_gen() :
            s, p = st.state, st.pos
            # insert
            for next_state in s.follow :
                update_state(SearchState(next_state, p), s.char, st, True)
            if p >= len(errstr) : 
                continue
            # enter
            for next_state in s.follow :
                update_state(SearchState(next_state, p + 1), s.char, st, s.char != errstr[p])
            # delete
            update_state(SearchState(s, p + 1), '', st, True)

        self.errstr:str = errstr
        self.cost:int = total_cost
        self.termini:Leaf = termini
        self.dist:[SearchState, SearchNode] = dist
        if not self.success :
            self.cost = -1

    @property
    def success(self) -> bool:
        return self.termini is not None
    
    def fix(self) -> Optional[str]:
        if self.termini is None: return None
        s = SearchState(self.termini, len(self.errstr))
        ret = []
        while len(self.dist[s].edges) :
            edge:SearchEdge = choice(self.dist[s].edges)
            op = edge.action
            ls = edge.prev
            ret.append(op)
            s = ls
        return ''.join(reversed(ret))
