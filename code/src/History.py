
class HistoryVertex:
    def __init__(self, vertex: Vertex, prev_vertex_1: Optional[Vertex] = None,
                 prev_vertex_2: Optional[Vertex] = None):
        self.vertex = vertex
        self.prev_vertex_1 = prev_vertex_1
        self.prev_vertex_2 = prev_vertex_2

    def __str__(self):
        return f'V: {self.vertex.id} V1: {self.prev_vertex_1.id} V2: {self.prev_vertex_2.id}'


class HistoryManager:
    def __init__(self, graph: MultiGraph):
        self.graph = graph
        self.base_state = copy.deepcopy(graph.get_state())
        self.history: List[HistoryVertex] = []
        self.current_step = -1

    def return_to_base_state(self):
        base_state_data = self.base_state
        self.graph.vertices = {}
        self.graph.edges = set()
        for vertex in base_state_data['vertices']:
            self.graph.add_vertex(vertex)
        self.graph.edges.update(base_state_data['edges'])
        self.current_step = -1

    def write_step(self, vertex: HistoryVertex):
        self.history.append(vertex)
        self.current_step = len(self.history) - 1

    def next_step(self):
        if self.current_step >= len(self.history) - 1:
            return
        if self.current_step == -1:
            self.current_step = 0
        else:
            self.current_step += 1
        self.graph.add_vertex(self.history[self.current_step].vertex)
        self.graph.remove_vertex(self.history[self.current_step].prev_vertex_1.id)
        self.graph.remove_vertex(self.history[self.current_step].prev_vertex_2.id)

    def prev_step(self):
        if self.current_step < 0:
            return
        if self.current_step == 0:
            self.return_to_base_state()
            return
        self.graph.remove_vertex(self.history[self.current_step].vertex.id)
        self.graph.add_vertex(self.history[self.current_step].prev_vertex_1)
        self.graph.add_vertex(self.history[self.current_step].prev_vertex_2)

        self.current_step -= 1


class LogManager:
    @staticmethod
    def setup_logging(log_file='graph_commands.log'):
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    @staticmethod
    def writeMerge(vertex1: Vertex, vertex2: Vertex, resultVertex: Vertex, datetime):
        log_message = f"Command: {GraphCommand.MERGE_COM:<10} | V1: {vertex1.name:<10} | V2: {vertex2.name:<10} | New_V: {resultVertex.name:<10} | Time: {datetime}"
        logging.info(log_message)

    @staticmethod
    def writeSplit(baseVertex: Vertex, vertex1: Vertex, vertex2: Vertex, datetime):
        log_message = f"Command: {GraphCommand.SPLIT_COM:<10} | Base V: {baseVertex.name:<10} | V1: {vertex1.name:<10} | V2: {vertex2.name:<10} | Time: {datetime}"
        logging.info(log_message)