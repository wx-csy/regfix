from collections import deque
from random import choice
from typing import List, Dict, Tuple, Deque, Optional
from dfa import DFA, State

class SearchState :
    def __init__(self, state:State, pos:int) :
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
    def __init__(self, dfa:DFA, errstr:str) :
        dist:Dict[SearchState, SearchNode] = {
            SearchState(dfa.initial, 0) : SearchNode(0, [])
        }
        charset:str = dfa.charset

        # 0/1 BFS: using deque
        deq:Deque[Tuple[SearchState, SearchEdge, bool]] = deque([(SearchState(dfa.initial, 0), None, False)])
        termini:List[State] = []
        total_cost:int = 2**63 - 1
        
        def update_state(s:SearchState, action:str, last:SearchState, one:bool) :
            nonlocal total_cost
            term = (s, SearchEdge(action, last), one)
            cost = dist[last].cost + int(one)
            if cost > total_cost : 
                return
            if s in dist and dist[s].cost < cost :
                return
            if one :
                deq.append(term)
            else :
                deq.appendleft(term)

        def dfs_gen() :
            nonlocal total_cost
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
                    if s.pos == len(errstr) and s.state.accept :
                        total_cost = cost
                        termini.append(s.state)
                yield s

        for st in dfs_gen() :
            s, p = st.state, st.pos
            # insert
            for ch in charset :
                update_state(SearchState(s.next(ch), p), ch, st, True)
            if p >= len(errstr) : 
                continue
            # enter
            for ch in charset :
                update_state(SearchState(s.next(ch), p + 1), ch, st, ch != errstr[p])
            # delete
            update_state(SearchState(s, p + 1), '', st, True)

        self.dfa = dfa
        self.errstr:str = errstr
        self.cost:int = total_cost
        self.termini:List[State] = termini
        self.dist:[SearchState, SearchNode] = dist

    @property
    def success(self) -> bool:
        return len(self.termini) > 0
    
    def fix(self) -> Optional[str]:
        if not self.termini : return None
        s = SearchState(choice(self.termini), len(self.errstr))
        ret = []
        while s != SearchState(self.dfa.initial, 0) :
            edge:SearchEdge = choice(self.dist[s].edges)
            op = edge.action
            ls = edge.prev
            ret.append(op)
            s = ls
        return ''.join(reversed(ret))
