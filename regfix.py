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
    def __init__(self, dfa:DFA, errstr:str, charset) :
        dis:Dict[SearchState, SearchNode] = {
            SearchState(dfa.initial, 0) : SearchNode(0, [])
        }
        # 0/1 BFS: using deque
        deq:Deque[SearchState] = deque([SearchState(dfa.initial, 0)])
        termini:List[State] = []
        total_cost:int = 2*63 - 1

        def update_state(s:SearchState, action:str, last:SearchState, one:bool) :
            cost = dis[last].cost + int(one)
            nonlocal total_cost
            if cost > total_cost : 
                return
            if s in dis :
                if dis[s].cost == cost :
                    dis[s].edges.append(SearchEdge(action, last))
            else :
                dis[s] = SearchNode(cost, [SearchEdge(action, last)])
                if s.pos < len(errstr) :
                    if one :
                        deq.append(s)
                    else :
                        deq.appendleft(s)
                elif s.state.acceptable :
                    total_cost = cost
                    termini.append(s.state)

        while deq :
            st = deq.popleft()
            s, p = st.state, st.pos
            print(s, p)
            # enter
            for ch in charset :
                update_state(SearchState(s.next(ch), p + 1), ch, st, ch != errstr[p])
            # insert
            for ch in charset :
                update_state(SearchState(s.next(ch), p), ch, st, True)
            # delete
            update_state(SearchState(s, p + 1), '', st, True)

        self.dfa = dfa
        self.errstr:str = errstr
        self.cost:int = total_cost
        self.termini:List[State] = termini
        self.dist:[SearchState, SearchNode] = dis

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
